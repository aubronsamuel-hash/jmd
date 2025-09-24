#!/usr/bin/env pwsh
[CmdletBinding()]
param(
  [string]$StepPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Info {
  param([string]$Message)
  Write-Host "[roadmap_guard] $Message"
}

$refPattern = 'Ref: (docs/roadmap/step-[0-9]{2}(?:\.[0-9]{2})?\.md)'
$gh = Get-Command gh -ErrorAction SilentlyContinue
$commitMessage = ''
$gitMessageLoaded = $false

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

if ($StepPath) {
  $StepPath = $StepPath.Trim()
  if ($StepPath) {
    Write-Info "Using provided StepPath: $StepPath"
  }
}

$prContext = Get-PrContext
if (-not $StepPath -and $prContext -and $prContext.Body) {
  $match = [regex]::Match([string]$prContext.Body, $refPattern)
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
  $StepPath = $env:ROADMAP_STEP_PATH.Trim()
  if ($StepPath) {
    Write-Info "Detected StepPath from env var: $StepPath"
  }
}

if (-not $StepPath) {
  throw "Unable to determine StepPath. Provide -StepPath, set ROADMAP_STEP_PATH, or ensure PR/commit contains 'Ref: docs/roadmap/step-XX.md'."
}

if ($StepPath) {
  $StepPath = $StepPath.Trim()
}

if ($StepPath -notmatch '^docs/roadmap/step-[0-9]{2}(?:\.[0-9]{2})?\.md$') {
  throw "StepPath '$StepPath' is not in the expected format docs/roadmap/step-XX[.YY].md."
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$normalized = $StepPath -replace '/', [System.IO.Path]::DirectorySeparatorChar
$targetPath = Join-Path $repoRoot $normalized
if (-not (Test-Path $targetPath)) {
  throw "Roadmap file '$StepPath' is missing."
}

$refLine = "Ref: $StepPath"
$commitMessage = Get-CommitMessage
$commitHasRef = $false
if ($commitMessage -and $commitMessage.Contains($refLine)) {
  $commitHasRef = $true
}

$prHasRef = $false
if ($prContext -and $prContext.Body) {
  if ([string]$prContext.Body -like "*${refLine}*") {
    $prHasRef = $true
  }
}

if (-not ($commitHasRef -or $prHasRef)) {
  throw "Neither the latest commit nor the PR body contains '$refLine'."
}

if ($commitHasRef) {
  Write-Info 'Latest commit contains roadmap reference.'
}
if ($prHasRef) {
  Write-Info 'PR body contains roadmap reference.'
}
Write-Info "Roadmap file validated: $StepPath"
