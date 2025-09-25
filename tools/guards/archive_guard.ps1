$ErrorActionPreference = "Stop"

$archiveRoot = ".codex"
if (-not (Test-Path $archiveRoot)) {
    throw ".codex directory missing."
}

$latestOutputPath = Join-Path $archiveRoot "latest/last_output.json"
if (-not (Test-Path $latestOutputPath)) {
    throw ".codex/latest/last_output.json missing."
}

$latestContent = Get-Content $latestOutputPath -Raw
if (-not $latestContent.Trim()) {
    throw ".codex/latest/last_output.json is empty."
}

try {
    $null = $latestContent | ConvertFrom-Json
} catch {
    throw ".codex/latest/last_output.json is not valid JSON."
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
