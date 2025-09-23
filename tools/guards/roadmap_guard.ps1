#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$pattern = 'Ref: (docs/roadmap/step-[0-9]{2}\.md)'
try {
  $commitMessage = git log -1 --pretty=%B
} catch {
  Write-Warning 'Impossible de lire le dernier commit. Assurez-vous que le depot Git est initialise.'
  exit 0
}

if ($commitMessage -match $pattern) {
  $path = $Matches[1]
  if (-not (Test-Path $path)) {
    Write-Error "Le fichier roadmap reference ($path) est introuvable."
    exit 1
  }
  Write-Host "Roadmap referencee: $path"
} else {
  Write-Error 'Le dernier commit ne contient pas la reference roadmap requise (Ref: docs/roadmap/step-XX.md).'
  exit 1
}

