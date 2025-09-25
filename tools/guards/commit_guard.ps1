$ErrorActionPreference = "Stop"

$log = git log -20 --pretty=format:"%H%x09%P%x09%s"
$commitMessage = $null
foreach ($line in $log -split "`n") {
    $parts = $line -split "`t"
    if ($parts.Length -ge 3) {
        $subject = $parts[2]
        if ($subject -notmatch '^Merge ') {
            $hash = $parts[0]
            $commitMessage = git log -1 --pretty=%B $hash
            break
        }
    }
}

if (-not $commitMessage) {
    $commitMessage = git log -1 --pretty=%B
}

if ($commitMessage -notmatch "Ref: docs/roadmap/") {
    throw "Latest non-merge commit missing roadmap reference."
}

Write-Host "commit_guard.ps1 passed"
