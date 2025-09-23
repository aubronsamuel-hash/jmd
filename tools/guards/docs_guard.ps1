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

$required = @(
  'docs/agents/README.md',
  'docs/CHANGELOG.md',
  'docs/codex/last_output.json'
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
$finalLine = 'VALIDATE? yes/no'

foreach ($file in $roadmapFiles) {
  $content = Get-Content -Path $file.FullName
  if (-not $content) {
    Write-Error "Le fichier ${($file.Name)} est vide."
    exit 1
  }
  $raw = $content -join "`n"
  if ($raw -notmatch '^# STEP [0-9]{2} - ') {
    Write-Error "Le fichier ${($file.Name)} doit commencer par un titre '# STEP XX - ...'."
    exit 1
  }
  foreach ($section in $requiredSections) {
    if ($raw -notmatch [regex]::Escape($section)) {
      Write-Error "Le fichier ${($file.Name)} ne contient pas la section obligatoire '$section'."
      exit 1
    }
  }
  $nonEmpty = @($content | ForEach-Object { $_.Trim() } | Where-Object { $_ })
  if (-not $nonEmpty) {
    Write-Error "Le fichier ${($file.Name)} ne contient pas de contenu valide."
    exit 1
  }
  $lastLine = $nonEmpty[-1]
  if ($lastLine -ne $finalLine) {
    Write-Error "La derniere ligne non vide de ${($file.Name)} doit etre '$finalLine'."
    exit 1
  }
  $linkPattern = "./$($file.Name)"
  if ($readmeContent -notmatch [regex]::Escape($linkPattern)) {
    Write-Error "Le fichier docs/roadmap/README.md doit referencer ${($file.Name)}."
    exit 1
  }
}

Write-Host 'Documentation verifiee: OK.'
