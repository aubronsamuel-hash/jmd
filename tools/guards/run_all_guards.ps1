#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$guards = @(
  'roadmap_guard.ps1',
  'docs_guard.ps1'
)

$failures = @()
foreach ($guard in $guards) {
  $path = Join-Path $scriptDir $guard
  try {
    Write-Host "Running guard: $guard"
    & $path
  } catch {
    Write-Error "Guard failed: $guard"
    $failures += $guard
  }
}

if ($failures.Count -gt 0) {
  Write-Error "Guards failed: $($failures -join ', ')"
  exit 1
}

Write-Host 'All guards passed.'

