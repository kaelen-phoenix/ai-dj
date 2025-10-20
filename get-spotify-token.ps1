# Script para obtener token de Spotify usando Client Credentials
# NOTA: Este token NO permite crear playlists, solo buscar canciones
# Para crear playlists necesitas OAuth 2.0 con el usuario

$clientId = "b568dcea222848aab3697ec6ca4195b7"
$clientSecret = "c1abfc0990574c68a4f8e9d4846190c1"

# Codificar credenciales en Base64
$credentials = "$clientId:$clientSecret"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($credentials)
$base64 = [System.Convert]::ToBase64String($bytes)

# Solicitar token
$headers = @{
    "Authorization" = "Basic $base64"
    "Content-Type" = "application/x-www-form-urlencoded"
}

$body = "grant_type=client_credentials"

try {
    $response = Invoke-RestMethod -Uri "https://accounts.spotify.com/api/token" -Method Post -Headers $headers -Body $body
    
    Write-Host "`n✅ Token obtenido exitosamente!" -ForegroundColor Green
    Write-Host "`nAccess Token:" -ForegroundColor Cyan
    Write-Host $response.access_token
    Write-Host "`nExpira en: $($response.expires_in) segundos ($($response.expires_in / 60) minutos)" -ForegroundColor Yellow
    Write-Host "`n⚠️  IMPORTANTE: Este token solo permite BUSCAR canciones, NO crear playlists." -ForegroundColor Red
    Write-Host "Para crear playlists necesitas OAuth 2.0 con autorización del usuario." -ForegroundColor Red
    
} catch {
    Write-Host "❌ Error obteniendo token:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}
