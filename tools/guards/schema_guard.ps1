$ErrorActionPreference = "Stop"

$contractPath = "schemas/contracts"
if (-not (Test-Path $contractPath)) {
    throw "schemas/contracts directory missing."
}

$files = Get-ChildItem -Path $contractPath -Filter *.json -File
if ($files.Count -eq 0) {
    throw "No contract JSON files found."
}

foreach ($file in $files) {
    $json = Get-Content $file.FullName -Raw | ConvertFrom-Json -AsHashtable
    if (-not $json.version) {
        throw "Contract $($file.Name) missing version field."
    }
    if (-not $json.name) {
        throw "Contract $($file.Name) missing name field."
    }
}

Write-Host "schema_guard.ps1 passed"
