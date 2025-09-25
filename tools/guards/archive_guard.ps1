$ErrorActionPreference = "Stop"

$archiveRoot = ".codex"
if (-not (Test-Path $archiveRoot)) {
    throw ".codex directory missing."
}

$indexPath = Join-Path $archiveRoot "index.json"
if (-not (Test-Path $indexPath)) {
    throw "index.json missing in archive."
}

$index = Get-Content $indexPath -Raw | ConvertFrom-Json -AsHashtable
if (-not $index.sessions -or $index.sessions.Count -eq 0) {
    throw "No sessions registered in archive index."
}

foreach ($session in $index.sessions) {
    $path = Join-Path $archiveRoot "archive/$($session.date)/session-$($session.session_id)"
    if (-not (Test-Path $path)) {
        throw "Session path $path missing."
    }
    foreach ($required in @("manifest.json", "last_output.json")) {
        $candidate = Join-Path $path $required
        if (-not (Test-Path $candidate)) {
            throw "Missing $required for session $($session.session_id)."
        }
    }
}

Write-Host "archive_guard.ps1 passed"
