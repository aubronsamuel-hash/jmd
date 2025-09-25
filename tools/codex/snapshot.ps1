Param(
    [Parameter(Mandatory = $true)][string]$SessionId,
    [Parameter(Mandatory = $true)][string]$Label,
    [string]$ArchiveRoot = ".codex"
)

$ErrorActionPreference = "Stop"

$sessionPath = Get-ChildItem -Path (Join-Path $ArchiveRoot "archive") -Recurse -Directory | Where-Object { $_.Name -eq "session-$SessionId" } | Select-Object -First 1
if (-not $sessionPath) {
    throw "Session $SessionId introuvable."
}

$dest = Join-Path $sessionPath.FullName ("snapshot-" + $Label + ".json")
$gitStatus = git status --short
$payload = [ordered]@{
    label = $Label
    created_at = (Get-Date -Format "o")
    git = [ordered]@{ status = $gitStatus }
}
$payload | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path $dest

Write-Host "Snapshot $Label enregistre pour $SessionId"
