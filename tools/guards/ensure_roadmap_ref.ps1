#!/usr/bin/env pwsh
[CmdletBinding()]
param(
  [string]$StepPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info {
  param([string]$Message)
  Write-Host "[ensure_roadmap_ref] $Message"
}

$refPattern = 'Ref: (docs/roadmap/step-[0-9]{2}\.md)'
$gh = Get-Command gh -ErrorAction SilentlyContinue
$commitMessage = ''
$gitMessageLoaded = $false

function Invoke-RoadmapRefEmptyCommit {
  param([string]$RefLine)

  $message = "chore(ci): ensure roadmap reference`n`n$RefLine"
  $args = @(
    '-c', 'user.name=roadmap-guard',
    '-c', 'user.email=roadmap-guard@users.noreply.github.com',
    '-c', 'commit.gpgsign=false',
    'commit', '--allow-empty', '-m', $message
  )

  & git @args | Out-Null
}

if ($StepPath) {
  $StepPath = $StepPath.Trim()
  if ($StepPath) {
    Write-Info "Using provided StepPath: $StepPath"
  }
}

function Get-CommitMessage {
  if (-not $script:gitMessageLoaded) {
    try {
      $script:commitMessage = git log -1 --pretty=%B
    } catch {
      $script:commitMessage = ''
    }
    $script:gitMessageLoaded = $true
  }
  return $script:commitMessage
}

function Get-PrNumber {
  if ($env:GITHUB_REF) {
    $match = [regex]::Match($env:GITHUB_REF, 'refs/pull/([0-9]+)/')
    if ($match.Success) { return $match.Groups[1].Value }
  }
  if ($env:GITHUB_REF_NAME) {
    $match = [regex]::Match($env:GITHUB_REF_NAME, '^([0-9]+)/(merge|head)$')
    if ($match.Success) { return $match.Groups[1].Value }
  }
  if ($env:GITHUB_EVENT_PATH -and (Test-Path $env:GITHUB_EVENT_PATH)) {
    try {
      $json = Get-Content $env:GITHUB_EVENT_PATH -Raw | ConvertFrom-Json
      if ($null -ne $json.number) {
        return [string]$json.number
      }
      if ($json.PSObject.Properties.Name -contains 'pull_request') {
        $pr = $json.pull_request
        if ($null -ne $pr -and $pr.PSObject.Properties.Name -contains 'number' -and $null -ne $pr.number) {
          return [string]$pr.number
        }
      }
    } catch {}
  }
  return $null
}

function Get-PrContext {
  if (-not $gh) { return $null }
  $prNumber = Get-PrNumber
  if (-not $prNumber) { return $null }
  try {
    $body = gh pr view $prNumber --json body -q .body
    return [pscustomobject]@{
      Number = $prNumber
      Body   = $body
    }
  } catch {
    return $null
  }
}

function Resolve-StepPathFromRoadmap {
$roadmapReadme = Join-Path 'docs' 'roadmap' 'ROADMAP.readme.md'
  if (-not (Test-Path $roadmapReadme)) { return $null }
  try {
    $content = Get-Content $roadmapReadme -Raw
  } catch {
    return $null
  }
  $match = [regex]::Match($content, 'step-([0-9]{2})\.md')
  if ($match.Success -and $match.Value) {
    return "docs/roadmap/$($match.Value)"
  }
  return $null
}

$prContext = Get-PrContext
if (-not $StepPath -and $prContext -and $prContext.Body) {
  $match = [regex]::Match($prContext.Body, $refPattern)
  if ($match.Success) {
    $StepPath = $match.Groups[1].Value
    Write-Info "Detected StepPath from PR body: $StepPath"
  }
}

if (-not $StepPath) {
  $message = Get-CommitMessage
  if ($message) {
    $match = [regex]::Match($message, $refPattern)
    if ($match.Success) {
      $StepPath = $match.Groups[1].Value
      Write-Info "Detected StepPath from last commit: $StepPath"
    }
  }
}

if (-not $StepPath -and $env:ROADMAP_STEP_PATH) {
  $StepPath = $env:ROADMAP_STEP_PATH
  Write-Info "Detected StepPath from env var: $StepPath"
}

if (-not $StepPath) {
  $resolved = Resolve-StepPathFromRoadmap
  if ($resolved) {
    $StepPath = $resolved
    Write-Info "Detected StepPath from docs/roadmap/ROADMAP.readme.md: $StepPath"
  }
}

if (-not $StepPath) {
  throw "Could not determine StepPath. Provide -StepPath, set ROADMAP_STEP_PATH, or ensure PR/commit contains 'Ref: docs/roadmap/step-XX.md'."
}

if ($StepPath) {
  $StepPath = $StepPath.Trim()
}
if ($StepPath -notmatch '^docs/roadmap/step-[0-9]{2}\.md$') {
  throw "StepPath '$StepPath' is not in the expected format docs/roadmap/step-XX.md."
}

$refLine = "Ref: $StepPath"

if ($prContext) {
  $existingBody = ''
  if ($null -ne $prContext.Body) {
    $existingBody = [string]$prContext.Body
  }
  if ($existingBody -like "*${refLine}*") {
    Write-Info 'PR body already contains roadmap ref.'
  } else {
    $trimmed = $existingBody.TrimEnd()
    if ($trimmed) {
      $newBody = "$trimmed`n`n$refLine"
    } else {
      $newBody = $refLine
    }
    $ghUpdateSucceeded = $false
    if ($gh) {
      try {
        gh pr edit $prContext.Number --body "$newBody" | Out-Null
        if ($LASTEXITCODE -eq 0 -and $?) {
          $ghUpdateSucceeded = $true
        }
      } catch {
        $ghUpdateSucceeded = $false
      }
    }

    if ($ghUpdateSucceeded) {
      Write-Info 'Appended roadmap ref to PR body.'
      $global:LASTEXITCODE = 0
    } else {
      Write-Info 'Failed to append to PR body. Falling back to empty commit.'
      $global:LASTEXITCODE = 0
      $message = Get-CommitMessage
      if (-not ($message -and $message.Contains($refLine))) {
        Write-Info 'Creating empty commit with roadmap ref...'
        Invoke-RoadmapRefEmptyCommit -RefLine $refLine
      } else {
        Write-Info 'Latest commit already contains roadmap ref. No action required.'
      }
    }
  }
} else {
  $message = Get-CommitMessage
  if ($message -and $message.Contains($refLine)) {
    Write-Info 'Latest commit already contains roadmap ref.'
  } else {
    Write-Info 'Creating empty commit with roadmap ref...'
    Invoke-RoadmapRefEmptyCommit -RefLine $refLine
  }
}
