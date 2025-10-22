$clientId = $env:SPOTIFY_CLIENT_ID
$clientSecret = $env:SPOTIFY_CLIENT_SECRET

if (-not $clientId) {
    $clientId = Read-Host "Enter SPOTIFY_CLIENT_ID"
}

if (-not $clientSecret) {
    $clientSecret = Read-Host "Enter SPOTIFY_CLIENT_SECRET"
}

if ([string]::IsNullOrWhiteSpace($clientId) -or [string]::IsNullOrWhiteSpace($clientSecret)) {
    Write-Host "❌ Both SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET are required." -ForegroundColor Red
    exit 1
}

$env:SPOTIFY_CLIENT_ID = $clientId
$env:SPOTIFY_CLIENT_SECRET = $clientSecret

Write-Host "✅ Variables configuradas correctamente!" -ForegroundColor Green
Write-Host "CLIENT_ID: $env:SPOTIFY_CLIENT_ID"
Write-Host "CLIENT_SECRET: $($clientSecret.Substring(0, [Math]::Min(6, $clientSecret.Length)))..."
