Param(
    [Parameter(Mandatory = $true)][string]$SessionId,
    [Parameter(Mandatory = $true)][string]$CommitHash,
    [string]$ArchiveRoot = ".codex"
)

$ErrorActionPreference = "Stop"

$sessionPath = Get-ChildItem -Path (Join-Path $ArchiveRoot "archive") -Recurse -Directory | Where-Object { $_.Name -eq "session-$SessionId" } | Select-Object -First 1
if (-not $sessionPath) {
    throw "Session $SessionId introuvable."
}

$commitData = git show $CommitHash --stat --pretty=fuller
$dest = Join-Path $sessionPath.FullName ("commit-" + $CommitHash + ".txt")
Set-Content -Path $dest -Encoding UTF8 -Value $commitData

Write-Host "Commit $CommitHash archive pour session $SessionId"
