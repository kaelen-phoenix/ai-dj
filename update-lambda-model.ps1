Write-Host "Actualizando modelo de Lambda..." -ForegroundColor Yellow

$functionName = "AI-DJ-Handler"
$newModel = "arcee.arcee-lite-v1:0"

Write-Host "Configurando modelo: $newModel" -ForegroundColor Cyan

# Actualizar variable de entorno
cmd /c "aws lambda update-function-configuration --function-name $functionName --environment `"Variables={BEDROCK_MODEL_ID=$newModel}`""

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Variable de entorno actualizada!" -ForegroundColor Green
    Write-Host "Espera 10 segundos para que se aplique..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Verificar
    Write-Host "`nVerificando configuración..." -ForegroundColor Yellow
    cmd /c "aws lambda get-function-configuration --function-name $functionName"
} else {
    Write-Host "`n❌ Error al actualizar" -ForegroundColor Red
}
