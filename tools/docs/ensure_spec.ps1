#!/usr/bin/env pwsh
[CmdletBinding()]
param(
  [string]$SourcePath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try {
  $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
  $repoRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
  $specRelative = 'docs/specs/spec-fonctionnelle-v0.1.md'
  $specPath = Join-Path $repoRoot $specRelative

  $specDir = Split-Path $specPath
  if (-not (Test-Path $specDir)) {
    New-Item -ItemType Directory -Force -Path $specDir | Out-Null
  }

  $shouldWrite = $false
  $buffer = ''
  if ($SourcePath) {
    $sourceFull = Resolve-Path -LiteralPath $SourcePath -ErrorAction SilentlyContinue
    if ($sourceFull) {
      $buffer = Get-Content -Path $sourceFull -Raw
      $shouldWrite = $true
    } else {
      Write-Host "WARN: fichier source '$SourcePath' introuvable."
    }
  }

  if (-not $shouldWrite -and (Test-Path $specPath)) {
    $buffer = Get-Content -Path $specPath -Raw
  }

  if (-not $shouldWrite -and -not $buffer) {
    $buffer = 'PLACEHOLDER: fournir la specification fonctionnelle v0.1.'
    $shouldWrite = $true
  }

  if ($shouldWrite) {
    [System.IO.File]::WriteAllText($specPath, $buffer, [System.Text.Encoding]::UTF8)
    Write-Host "Spec ecrite vers $specRelative"
  }

  if (-not (Test-Path $specPath)) {
    throw "Le fichier $specRelative est introuvable apres ecriture."
  }

  $specContent = Get-Content -Path $specPath -Raw
  $useful = ($specContent -replace '\s', '')
  if ([string]::IsNullOrWhiteSpace($useful) -or $useful.Length -lt 50) {
    throw "La specification $specRelative doit contenir au moins 50 caracteres utiles."
  }

  $agentDefinitions = @(
    @{ Path = 'docs/agents/AGENT.index.md'; Lines = @('Source unique de la verite: docs/specs/spec-fonctionnelle-v0.1.md') },
    @{ Path = 'docs/agents/AGENT.backend.md'; Lines = @('SUT: docs/specs/spec-fonctionnelle-v0.1.md', 'Les schemas, services et regles metier doivent respecter les modules et workflows de la spec.') },
    @{ Path = 'docs/agents/AGENT.frontend.md'; Lines = @('SUT: docs/specs/spec-fonctionnelle-v0.1.md', 'Les vues (planning, paie, materiel, notifications) et interactions (drag-drop, timeline) suivent la spec.') },
    @{ Path = 'docs/agents/AGENT.devops.md'; Lines = @('SUT: docs/specs/spec-fonctionnelle-v0.1.md', 'Les guards/CI verifient la presence et la reference de la spec.') },
    @{ Path = 'docs/agents/AGENT.docs.md'; Lines = @('SUT: docs/specs/spec-fonctionnelle-v0.1.md', 'Tous les documents generes doivent rester alignes avec la spec.') }
  )

  foreach ($agent in $agentDefinitions) {
    $agentPath = Join-Path $repoRoot $agent.Path
    if (-not (Test-Path $agentPath)) {
      Write-Host "SKIP: $($agent.Path) absent"
      continue
    }
    $original = Get-Content -Path $agentPath -Raw
    $missing = @()
    foreach ($line in $agent.Lines) {
      if ($original -notmatch [regex]::Escape($line)) {
        $missing += $line
      }
    }
    if ($missing.Count -gt 0) {
      $prefix = [string]::Join("`n", $missing)
      if ([string]::IsNullOrWhiteSpace($original)) {
        $updated = $prefix
      } else {
        $updated = "$prefix`n`n$original"
      }
      [System.IO.File]::WriteAllText($agentPath, $updated, [System.Text.Encoding]::UTF8)
      Write-Host "Injected SUT markers in $($agent.Path)"
    }
  }

  exit 0
} catch {
  Write-Error $_.Exception.Message
  exit 1
}
