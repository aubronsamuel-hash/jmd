Param(
    [Parameter(Mandatory = $true)][string]$SessionId,
    [Parameter(Mandatory = $true)][string]$Checksum,
    [string]$ArchiveRoot = ".codex"
)

$ErrorActionPreference = "Stop"

$sessionPath = Get-ChildItem -Path (Join-Path $ArchiveRoot "archive") -Recurse -Directory | Where-Object { $_.Name -eq "session-$SessionId" } | Select-Object -First 1
if (-not $sessionPath) {
    throw "Session $SessionId introuvable."
}

$diffFile = Get-ChildItem -Path $sessionPath.FullName -Filter ("diff-" + $Checksum + ".patch") -File | Select-Object -First 1
if (-not $diffFile) {
    throw "Checksum $Checksum introuvable pour session $SessionId."
}

$expected = $Checksum.ToLower()
$content = Get-Content $diffFile.FullName -Raw
$actual = [BitConverter]::ToString((New-Object -TypeName System.Security.Cryptography.SHA256Managed).ComputeHash([Text.Encoding]::UTF8.GetBytes($content))).Replace("-", "").ToLower()
if ($actual -ne $expected) {
    throw "Checksum mismatch: attendu $expected, obtenu $actual."
}

$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$stream = New-Object System.IO.MemoryStream(,$bytes)
try {
    git apply --whitespace=nowarn --stat $diffFile.FullName | Out-Null
    git apply --whitespace=nowarn $diffFile.FullName
} finally {
    $stream.Dispose()
}

Write-Host "Diff $Checksum rejoue pour session $SessionId"
