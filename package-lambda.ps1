# Script para empaquetar Lambda con dependencias
Write-Host "Empaquetando Lambda con dependencias..." -ForegroundColor Cyan

# Crear directorio temporal
$tempDir = "lambda_package"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Copiar codigo de Lambda
Copy-Item -Path "lambda_src\*.py" -Destination $tempDir

# Instalar dependencias en el directorio
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
pip install -r lambda_src\requirements.txt -t $tempDir --upgrade

Write-Host "Lambda empaquetada en: $tempDir" -ForegroundColor Green
