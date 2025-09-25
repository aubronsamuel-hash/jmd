Param(
    [Parameter(Mandatory = $true)][string]$SessionId,
    [string]$ArchiveRoot = ".codex"
)

$ErrorActionPreference = "Stop"

$sessionPath = Get-ChildItem -Path (Join-Path $ArchiveRoot "archive") -Recurse -Directory | Where-Object { $_.Name -eq "session-$SessionId" } | Select-Object -First 1
if (-not $sessionPath) {
    throw "Session $SessionId introuvable."
}

$diff = git diff
$hash = [BitConverter]::ToString((New-Object -TypeName System.Security.Cryptography.SHA256Managed).ComputeHash([Text.Encoding]::UTF8.GetBytes($diff))).Replace("-", "").ToLower()
$dest = Join-Path $sessionPath.FullName ("diff-" + $hash + ".patch")
Set-Content -Path $dest -Encoding UTF8 -Value $diff

$logPath = Join-Path $sessionPath.FullName "logs/diff-log.json"
$entry = [ordered]@{
    captured_at = (Get-Date -Format "o")
    checksum = $hash
    file = (Split-Path -Leaf $dest)
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

Write-Host "Diff capture with checksum $hash"
