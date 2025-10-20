# Obtener token de Spotify usando Client Credentials
# IMPORTANTE: Este token NO permite crear playlists, solo buscar canciones

$clientId = "b568dcea222848aab3697ec6ca4195b7"
$clientSecret = "c1abfc0990574c68a4f8e9d4846190c1"

Write-Host "Obteniendo token de Spotify..." -ForegroundColor Cyan

# Codificar credenciales en Base64
$credentials = "${clientId}:${clientSecret}"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($credentials)
$base64 = [System.Convert]::ToBase64String($bytes)

# Hacer peticion
$headers = @{
    "Authorization" = "Basic $base64"
    "Content-Type" = "application/x-www-form-urlencoded"
}

$body = "grant_type=client_credentials"

try {
    $response = Invoke-RestMethod -Uri "https://accounts.spotify.com/api/token" -Method Post -Headers $headers -Body $body
    
    Write-Host "`n[SUCCESS] Token obtenido!" -ForegroundColor Green
    Write-Host "`nAccess Token:" -ForegroundColor Yellow
    Write-Host $response.access_token
    Write-Host "`nExpira en: $($response.expires_in) segundos" -ForegroundColor Cyan
    
    # Guardar en archivo
    $response.access_token | Out-File -FilePath "spotify_token_client.txt" -NoNewline
    Write-Host "`n[SAVED] Token guardado en: spotify_token_client.txt" -ForegroundColor Green
    
    Write-Host "`n[WARNING] Este token SOLO permite buscar canciones." -ForegroundColor Red
    Write-Host "[WARNING] NO puede crear playlists porque no esta asociado a un usuario." -ForegroundColor Red
    Write-Host "`nPara crear playlists necesitas OAuth 2.0 con autorizacion de usuario." -ForegroundColor Yellow
    
} catch {
    Write-Host "`n[ERROR] Error obteniendo token:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
