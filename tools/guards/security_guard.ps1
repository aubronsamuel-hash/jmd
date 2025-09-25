$ErrorActionPreference = "Stop"

$vulnFile = "reports/security/dependencies.json"
$threshold = 7.0
if (Test-Path $vulnFile) {
    $report = Get-Content $vulnFile -Raw | ConvertFrom-Json
    foreach ($finding in $report) {
        if ($finding.cvss -ge $threshold) {
            throw "Security vulnerability above threshold detected: $($finding.id)"
        }
    }
    Write-Host "security_guard.ps1 passed without critical findings."
} else {
    Write-Host "No security report found, ensure scans executed in CI."
}
