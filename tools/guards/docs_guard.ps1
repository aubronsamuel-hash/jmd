#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $repoRoot
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
$roadmapFiles = Get-ChildItem -Path $roadmapDir -Filter 'step-*.md' -ErrorAction SilentlyContinue
if (-not $roadmapFiles) {
  Write-Error 'Aucun fichier roadmap step-XX.md trouve.'
  exit 1
}

foreach ($file in $roadmapFiles) {
  $content = Get-Content -Path $file.FullName -Raw
  if ($content -notmatch 'VALIDATE\?') {
    Write-Error "Le fichier ${($file.Name)} ne contient pas le bloc VALIDATE?."
    exit 1
  }
}

Write-Host 'Documentation verifiee: OK.'

