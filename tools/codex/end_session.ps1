Param(
    [Parameter(Mandatory = $true)][string]$SessionId,
    [string]$ArchiveRoot = ".codex"
)

$ErrorActionPreference = "Stop"

$sessionPath = Get-ChildItem -Path (Join-Path $ArchiveRoot "archive") -Recurse -Directory | Where-Object { $_.Name -eq "session-$SessionId" } | Select-Object -First 1
if (-not $sessionPath) {
    throw "Session $SessionId introuvable dans $ArchiveRoot."
}

$latest = Get-Content (Join-Path $sessionPath.FullName "last_output.json") -Raw | ConvertFrom-Json -AsHashtable
$latest.status = "closed"
$latest.last_update = (Get-Date -Format "o")
$latest | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path (Join-Path $sessionPath.FullName "last_output.json")
$latest | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path (Join-Path $ArchiveRoot "latest/last_output.json")

Write-Host "Session $SessionId fermee."
