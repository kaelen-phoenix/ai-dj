# Script para configurar variables de entorno de Spotify
# Ejecutar como: .\set-env.ps1

Write-Host "🔧 Configurando variables de entorno de Spotify..." -ForegroundColor Cyan

# Client ID (ya conocido)
$clientId = "b568dcea222848aab3697ec6ca4195b7"

# Client Secret - REEMPLAZAR CON EL VALOR REAL
$clientSecret = Read-Host "Ingresa el SPOTIFY_CLIENT_SECRET"

if ([string]::IsNullOrWhiteSpace($clientSecret)) {
    Write-Host "❌ Client Secret no puede estar vacío" -ForegroundColor Red
    exit 1
}

# Configurar para la sesión actual
$env:SPOTIFY_CLIENT_ID = $clientId
$env:SPOTIFY_CLIENT_SECRET = $clientSecret

Write-Host "✅ Variables configuradas para esta sesión:" -ForegroundColor Green
Write-Host "   SPOTIFY_CLIENT_ID: $clientId" -ForegroundColor White
Write-Host "   SPOTIFY_CLIENT_SECRET: $($clientSecret.Substring(0, [Math]::Min(10, $clientSecret.Length)))..." -ForegroundColor White

Write-Host ""
Write-Host "⚠️  Estas variables son temporales (solo para esta sesión de PowerShell)" -ForegroundColor Yellow
Write-Host ""
Write-Host "📝 Para hacerlas permanentes:" -ForegroundColor Cyan
Write-Host "   1. Busca 'Variables de entorno' en Windows"
Write-Host "   2. Click en 'Variables de entorno'"
Write-Host "   3. En 'Variables del sistema', click 'Nueva'"
Write-Host "   4. Agrega:"
Write-Host "      - Nombre: SPOTIFY_CLIENT_ID"
Write-Host "      - Valor: $clientId"
Write-Host "   5. Agrega otra:"
Write-Host "      - Nombre: SPOTIFY_CLIENT_SECRET"
Write-Host "      - Valor: [tu client secret]"
Write-Host ""
Write-Host "🚀 Ahora puedes desplegar con: cdk deploy" -ForegroundColor Green
