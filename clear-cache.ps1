Write-Host "Limpiando cache de CloudFront..." -ForegroundColor Yellow

$distributionId = "E25KR386LY1S19"

# Crear invalidación usando cmd para evitar problemas con PowerShell
cmd /c "aws cloudfront create-invalidation --distribution-id $distributionId --paths `"/*`""

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Cache invalidado exitosamente!" -ForegroundColor Green
    Write-Host "Espera 1-2 minutos para que se complete." -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Error al invalidar cache" -ForegroundColor Red
}
