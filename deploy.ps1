# Script de despliegue para AI DJ
Write-Host "🚀 Iniciando despliegue de AI DJ..." -ForegroundColor Cyan

# Configurar variables de entorno
$env:SPOTIFY_CLIENT_ID = "b568dcea222848aab3697ec6ca4195b7"
$env:SPOTIFY_CLIENT_SECRET = "c1abfc0990574c68a4f8e9d4846190c1"

# Activar entorno virtual
Write-Host "`n📦 Activando entorno virtual..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Verificar que el entorno está activado
Write-Host "`n✅ Verificando configuración..." -ForegroundColor Green
python --version
aws sts get-caller-identity

# Bootstrap (solo primera vez)
Write-Host "`n🔧 Ejecutando CDK bootstrap..." -ForegroundColor Yellow
cdk bootstrap

# Sintetizar
Write-Host "`n🔨 Sintetizando stack..." -ForegroundColor Yellow
cdk synth

# Desplegar
Write-Host "`n🚀 Desplegando a AWS..." -ForegroundColor Yellow
cdk deploy --require-approval never --outputs-file outputs.json

Write-Host "`n✅ ¡Despliegue completado!" -ForegroundColor Green
Write-Host "Ver outputs en: outputs.json" -ForegroundColor Cyan
