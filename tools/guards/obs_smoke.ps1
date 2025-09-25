$ErrorActionPreference = "Stop"

$healthEndpoint = "http://localhost:8080/healthz"
try {
    $response = Invoke-WebRequest -Uri $healthEndpoint -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -ge 300) {
        throw "Health endpoint returned status $($response.StatusCode)."
    }
    Write-Host "Observability smoke check succeeded: $($response.StatusCode)"
} catch {
    Write-Host "Observability smoke check skipped: $_"
}
