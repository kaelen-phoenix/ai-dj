# Script para probar la API de AI DJ
$apiEndpoint = "https://08zk6n0hhf.execute-api.us-east-1.amazonaws.com/playlist"

# Nota: Necesitas un access token valido de Spotify
# Para obtenerlo, implementa OAuth 2.0 o usa la Spotify Web Console

$body = @{
    user_id = "test_user_hackathon"
    prompt = "Musica energetica para hacer ejercicio, rock y electronica"
    spotify_access_token = "NECESITAS_TOKEN_REAL_AQUI"
} | ConvertTo-Json

Write-Host "Probando API de AI DJ..." -ForegroundColor Cyan
Write-Host "Endpoint: $apiEndpoint" -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri $apiEndpoint -Method Post -Body $body -ContentType "application/json"
    Write-Host "Respuesta exitosa:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error en la peticion:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "Detalles del error:" -ForegroundColor Yellow
    $_.ErrorDetails.Message
}
