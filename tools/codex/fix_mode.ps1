Param(
    [Parameter(Mandatory = $true)][string]$SessionId,
    [Parameter(Mandatory = $true)][string]$Ref,
    [string]$ArchiveRoot = ".codex"
)

$ErrorActionPreference = "Stop"

$sessionPath = Get-ChildItem -Path (Join-Path $ArchiveRoot "archive") -Recurse -Directory | Where-Object { $_.Name -eq "session-$SessionId" } | Select-Object -First 1
if (-not $sessionPath) {
    throw "Session $SessionId introuvable."
}

$logPath = Join-Path $sessionPath.FullName "logs/fix-log.json"
$entry = [ordered]@{
    ref = $Ref
    started_at = (Get-Date -Format "o")
}

if (Test-Path $logPath) {
    $history = Get-Content $logPath -Raw | ConvertFrom-Json -AsHashtable
    $history.entries = @($history.entries + @($entry))
} else {
    $history = [ordered]@{
        session = $SessionId
        entries = @($entry)
    }
}

$history | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 -Path $logPath

Write-Host "Mode FIX initie pour $Ref dans session $SessionId"
