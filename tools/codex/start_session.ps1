Param(
    [Parameter(Mandatory = $true)][string]$StepRef,
    [string]$ArchiveRoot = ".codex"
)

$ErrorActionPreference = "Stop"

$sessionId = [guid]::NewGuid().ToString()
$today = (Get-Date -Format "yyyy-MM-dd")
$sessionPath = Join-Path -Path $ArchiveRoot -ChildPath "archive/$today/session-$sessionId"
New-Item -ItemType Directory -Path (Join-Path $sessionPath "logs") -Force | Out-Null

$manifest = [ordered]@{
    session_id = $sessionId
    date = $today
    step_ref = $StepRef
    archive_version = "1.0.0"
}

$manifestPath = Join-Path $sessionPath "manifest.json"
$manifest | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path $manifestPath

$latestPath = Join-Path $ArchiveRoot "latest"
New-Item -ItemType Directory -Path $latestPath -Force | Out-Null

$state = [ordered]@{
    step = $StepRef
    status = "in-progress"
    session = $sessionId
    last_update = (Get-Date -Format "o")
}

$state | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path (Join-Path $sessionPath "last_output.json")
$state | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path (Join-Path $latestPath "last_output.json")

$indexPath = Join-Path $ArchiveRoot "index.json"
if (Test-Path $indexPath) {
    $existing = Get-Content $indexPath -Raw | ConvertFrom-Json -AsHashtable
    $existing.sessions = @($existing.sessions + @([ordered]@{ date = $today; session_id = $sessionId; step_ref = $StepRef }))
} else {
    $existing = [ordered]@{
        archive_version = "1.0.0"
        sessions = @([ordered]@{ date = $today; session_id = $sessionId; step_ref = $StepRef })
    }
}

$existing | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path $indexPath

Write-Host "Started Codex session $sessionId for $StepRef"
