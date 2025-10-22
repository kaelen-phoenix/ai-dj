# Invalidar cache de CloudFront
Write-Host "Obteniendo distribuciones de CloudFront..." -ForegroundColor Cyan

$distributions = aws cloudfront list-distributions | ConvertFrom-Json
$targetDomain = "d1z4qoq01pmvv3.cloudfront.net"

foreach ($item in $distributions.DistributionList.Items) {
    if ($item.DomainName -eq $targetDomain) {
        $distId = $item.Id
        Write-Host "Encontrado: $distId" -ForegroundColor Green
        Write-Host "Invalidando cache..." -ForegroundColor Yellow
        
        aws cloudfront create-invalidation --distribution-id $distId --paths "/*"
        
        Write-Host "Cache invalidado! Los cambios estarán visibles en 1-2 minutos." -ForegroundColor Green
        exit 0
    }
}

Write-Host "No se encontró la distribución" -ForegroundColor Red
