#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$docsDir = Join-Path $repoRoot 'docs'

if (-not (Test-Path $docsDir)) {
  Write-Error 'Le dossier docs/ est manquant.'
  exit 1
}

$specRelative = 'docs/specs/spec-fonctionnelle-v0.1.md'
$specPath = Join-Path $repoRoot $specRelative
if (-not (Test-Path $specPath)) {
  Write-Error "Le fichier obligatoire $specRelative est absent."
  exit 1
}

try {
  $specContent = Get-Content -Path $specPath -Raw
} catch {
  Write-Error "Impossible de lire $specRelative."
  exit 1
}

$useful = ($specContent -replace '\s', '')
if ([string]::IsNullOrWhiteSpace($useful) -or $useful.Length -lt 50) {
  Write-Error 'La specification fonctionnelle doit contenir au moins 50 caracteres utiles.'
  exit 1
}

function Invoke-Git {
  param(
    [string[]]$Arguments
  )

  try {
    $result = & git @Arguments 2>$null
    if ($LASTEXITCODE -eq 0 -and $result) {
      return [string]::Join("`n", $result)
    }
  } catch {
    return ''
  }
  return ''
}

function Add-ChangedFile {
  param(
    [System.Collections.Generic.HashSet[string]]$Set,
    [string]$File
  )

  if (-not $File) { return }
  $normalized = $File.Trim()
  if (-not $normalized) { return }
  $normalized = $normalized -replace '[\\]', '/'
  if ($normalized -like 'docs/agents/AGENT*.md') {
    $Set.Add($normalized) | Out-Null
  }
}

function Get-DiffForFile {
  param(
    [string]$File
  )

  $chunks = @()
  $diffWorking = Invoke-Git @('diff', '--color=never', '-U5000', '--', $File)
  if ($diffWorking) { $chunks += $diffWorking }
  $diffStaged = Invoke-Git @('diff', '--color=never', '-U5000', '--staged', '--', $File)
  if ($diffStaged) { $chunks += $diffStaged }

  $hasParent = $false
  try {
    & git rev-parse --verify HEAD^ 1>$null 2>$null
    if ($LASTEXITCODE -eq 0) {
      $hasParent = $true
    }
  } catch {
    $hasParent = $false
  }

  if ($hasParent) {
    $diffCommit = Invoke-Git @('diff', '--color=never', '-U5000', 'HEAD^..HEAD', '--', $File)
    if ($diffCommit) { $chunks += $diffCommit }
  } else {
    $diffCommit = Invoke-Git @('show', '--color=never', '-U5000', 'HEAD', '--', $File)
    if ($diffCommit) { $chunks += $diffCommit }
  }

  return ($chunks -join "`n").Trim()
}

$agentRequirements = @(
  @{ Path = 'docs/agents/AGENT.md'; Marker = 'Source unique de la verite: docs/specs/spec-fonctionnelle-v0.1.md'; DiffMarker = $null },
  @{ Path = 'docs/agents/AGENT.backend.md'; Marker = 'SUT: docs/specs/spec-fonctionnelle-v0.1.md'; DiffMarker = 'SUT: docs/specs/spec-fonctionnelle-v0.1.md' },
  @{ Path = 'docs/agents/AGENT.frontend.md'; Marker = 'SUT: docs/specs/spec-fonctionnelle-v0.1.md'; DiffMarker = 'SUT: docs/specs/spec-fonctionnelle-v0.1.md' },
  @{ Path = 'docs/agents/AGENT.devops.md'; Marker = 'SUT: docs/specs/spec-fonctionnelle-v0.1.md'; DiffMarker = 'SUT: docs/specs/spec-fonctionnelle-v0.1.md' },
  @{ Path = 'docs/agents/AGENT.docs.md'; Marker = 'SUT: docs/specs/spec-fonctionnelle-v0.1.md'; DiffMarker = 'SUT: docs/specs/spec-fonctionnelle-v0.1.md' }
)

foreach ($req in $agentRequirements) {
  $fullPath = Join-Path $repoRoot $req.Path
  if (-not (Test-Path $fullPath)) {
    Write-Error "Le fichier obligatoire $($req.Path) est manquant."
    exit 1
  }
  $content = Get-Content -Path $fullPath -Raw
  if ($content -notmatch [regex]::Escape($req.Marker)) {
    Write-Error "Le fichier $($req.Path) doit contenir la ligne '$($req.Marker)'."
    exit 1
  }
}

$changedAgents = New-Object 'System.Collections.Generic.HashSet[string]' ([System.StringComparer]::OrdinalIgnoreCase)

$diffSources = @(
  @('diff', '--name-only'),
  @('diff', '--name-only', '--staged'),
  @('show', '--name-only', '--pretty=format:', 'HEAD')
)

foreach ($args in $diffSources) {
  $list = Invoke-Git $args
  if (-not $list) { continue }
  foreach ($line in $list -split "`n") {
    Add-ChangedFile -Set $changedAgents -File $line
  }
}

foreach ($req in $agentRequirements) {
  if (-not $req.DiffMarker) { continue }
  if (-not $changedAgents.Contains($req.Path)) { continue }
  $diffText = Get-DiffForFile -File $req.Path
  if (-not $diffText) { continue }
  if ($diffText -notmatch [regex]::Escape($req.DiffMarker)) {
    Write-Error "Les modifications de $($req.Path) doivent mentionner '$($req.DiffMarker)' dans le diff."
    exit 1
  }
}

$required = @(
  'docs/agents/README.md',
  'docs/CHANGELOG.md',
  'docs/codex/last_output.json',
  'docs/compliance/audit-register.md'
)

$missing = @()
foreach ($item in $required) {
  $path = Join-Path $repoRoot $item
  if (-not (Test-Path $path)) {
    $missing += $item
  }
}

if ($missing.Count -gt 0) {
  Write-Error "Fichiers documentaires manquants: $($missing -join ', ')"
  exit 1
}

$roadmapDir = Join-Path $docsDir 'roadmap'
$roadmapFiles = Get-ChildItem -Path $roadmapDir -Filter 'step-*.md' -File -ErrorAction SilentlyContinue | Sort-Object Name
if (-not $roadmapFiles) {
  Write-Error 'Aucun fichier roadmap step-XX.md trouve.'
  exit 1
}

$roadmapReadme = Join-Path $roadmapDir 'README.md'
if (-not (Test-Path $roadmapReadme)) {
  Write-Error 'Le fichier docs/roadmap/README.md est manquant.'
  exit 1
}
$readmeContent = Get-Content -Path $roadmapReadme -Raw

$requiredSections = @(
  '## SUMMARY',
  '## GOALS',
  '## CHANGES',
  '## TESTS',
  '## CI',
  '## ARCHIVE'
)
$allowedFinalLines = @('VALIDATE? yes/no', 'VALIDATE? yes', 'VALIDATE? no')

foreach ($file in $roadmapFiles) {
  $content = Get-Content -Path $file.FullName
  if (-not $content) {
    Write-Error "Le fichier $($file.Name) est vide."
    exit 1
  }
  $raw = $content -join "`n"
  if ($raw -notmatch '^# STEP [0-9]{2} - ') {
    Write-Error "Le fichier $($file.Name) doit commencer par un titre '# STEP XX - ...'."
    exit 1
  }
  foreach ($section in $requiredSections) {
    if ($raw -notmatch [regex]::Escape($section)) {
      Write-Error "Le fichier $($file.Name) ne contient pas la section obligatoire '$section'."
      exit 1
    }
  }
  $nonEmpty = @($content | ForEach-Object { $_.Trim() } | Where-Object { $_ })
  if (-not $nonEmpty) {
    Write-Error "Le fichier $($file.Name) ne contient pas de contenu valide."
    exit 1
  }
  $lastLine = $nonEmpty[-1]
  if ($allowedFinalLines -notcontains $lastLine) {
    Write-Error "La derniere ligne non vide de $($file.Name) doit etre l'une des valeurs 'VALIDATE? yes/no', 'VALIDATE? yes' ou 'VALIDATE? no'."
    exit 1
  }
  $linkPattern = "./$($file.Name)"
  if ($readmeContent -notmatch [regex]::Escape($linkPattern)) {
    Write-Error "Le fichier docs/roadmap/README.md doit referencer $($file.Name)."
    exit 1
  }
}

Write-Host 'Documentation verifiee: OK.'
