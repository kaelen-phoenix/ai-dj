# Probar la API con el token obtenido
$apiEndpoint = "https://08zk6n0hhf.execute-api.us-east-1.amazonaws.com/playlist"

# Leer token del archivo
$token = Get-Content "spotify_token_client.txt" -Raw

Write-Host "Probando API de AI DJ..." -ForegroundColor Cyan
Write-Host "Endpoint: $apiEndpoint" -ForegroundColor Yellow
Write-Host "Token: $($token.Substring(0,20))..." -ForegroundColor Gray
Write-Host ""

$body = @{
    user_id = "test_user_hackathon"
    prompt = "Musica energetica para hacer ejercicio, rock y electronica"
    spotify_access_token = $token.Trim()
} | ConvertTo-Json

Write-Host "Enviando peticion..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri $apiEndpoint -Method Post -Body $body -ContentType "application/json"
    
    Write-Host "`n[SUCCESS] Respuesta recibida:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10 | Write-Host
    
} catch {
    Write-Host "`n[ERROR] Error en la peticion:" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host "`nDetalles del error:" -ForegroundColor Yellow
        $_.ErrorDetails.Message | ConvertFrom-Json | ConvertTo-Json -Depth 10 | Write-Host
    } else {
        Write-Host $_.Exception.Message
    }
}
