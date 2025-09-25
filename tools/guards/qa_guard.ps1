$ErrorActionPreference = "Stop"

$coverageFile = "coverage/summary.json"
if (Test-Path $coverageFile) {
    $summary = Get-Content $coverageFile -Raw | ConvertFrom-Json -AsHashtable
    $lineCoverage = [double]($summary.total.lines.pct)
    if ($lineCoverage -lt 80) {
        throw "Line coverage $lineCoverage below threshold 80."
    }
    Write-Host "QA coverage check: $lineCoverage%"
} else {
    Write-Host "Coverage summary not found, skipping enforcement."
}

Write-Host "qa_guard.ps1 passed"
