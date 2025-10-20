# Script para crear distribucion CloudFront con HTTPS

Write-Host "Configurando CloudFront con HTTPS para AI DJ..." -ForegroundColor Cyan

$bucketName = "ai-dj-frontend-4064"
$bucketWebsite = "$bucketName.s3-website-us-east-1.amazonaws.com"

Write-Host "`n[INFO] Creando distribucion CloudFront..." -ForegroundColor Yellow
Write-Host "Esto puede tomar 10-15 minutos..." -ForegroundColor Gray

# Crear configuracion de CloudFront
$config = @"
{
    "CallerReference": "ai-dj-$(Get-Date -Format 'yyyyMMddHHmmss')",
    "Comment": "AI DJ Frontend Distribution",
    "Enabled": true,
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-$bucketName",
                "DomainName": "$bucketWebsite",
                "CustomOriginConfig": {
                    "HTTPPort": 80,
                    "HTTPSPort": 443,
                    "OriginProtocolPolicy": "http-only"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-$bucketName",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "ForwardedValues": {
            "QueryString": false,
            "Cookies": {
                "Forward": "none"
            }
        },
        "MinTTL": 0,
        "DefaultTTL": 86400,
        "MaxTTL": 31536000,
        "Compress": true
    },
    "DefaultRootObject": "index.html",
    "CustomErrorResponses": {
        "Quantity": 1,
        "Items": [
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 300
            }
        ]
    },
    "PriceClass": "PriceClass_100"
}
"@

$config | Out-File -FilePath "cloudfront-config.json" -Encoding UTF8

Write-Host "`nCreando distribucion..." -ForegroundColor Yellow
$result = aws cloudfront create-distribution --distribution-config file://cloudfront-config.json 2>&1

if ($LASTEXITCODE -eq 0) {
    $distribution = $result | ConvertFrom-Json
    $cloudfrontUrl = $distribution.Distribution.DomainName
    $distributionId = $distribution.Distribution.Id
    
    Write-Host "`n============================================" -ForegroundColor Green
    Write-Host "[SUCCESS] CloudFront creado!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "`nURL HTTPS de tu aplicacion:" -ForegroundColor Cyan
    Write-Host "https://$cloudfrontUrl" -ForegroundColor White
    Write-Host "`nDistribution ID:" -ForegroundColor Cyan
    Write-Host $distributionId -ForegroundColor White
    Write-Host "`nEstado: Desplegando (10-15 minutos)..." -ForegroundColor Yellow
    Write-Host "`n============================================" -ForegroundColor Green
    Write-Host "SIGUIENTE PASO:" -ForegroundColor Yellow
    Write-Host "1. Espera 10-15 minutos a que CloudFront se despliegue" -ForegroundColor White
    Write-Host "2. Ve a: https://developer.spotify.com/dashboard" -ForegroundColor White
    Write-Host "3. Abre tu app 'AI DJ' > Settings" -ForegroundColor White
    Write-Host "4. En 'Redirect URIs' agrega:" -ForegroundColor White
    Write-Host "   https://$cloudfrontUrl/" -ForegroundColor Cyan
    Write-Host "5. Guarda los cambios" -ForegroundColor White
    Write-Host "6. Abre tu app en: https://$cloudfrontUrl" -ForegroundColor White
    Write-Host "============================================" -ForegroundColor Green
    
    # Guardar info
    @{
        bucket = $bucketName
        cloudfront_url = "https://$cloudfrontUrl"
        distribution_id = $distributionId
    } | ConvertTo-Json | Out-File -FilePath "cloudfront-deployment.json"
    
    Write-Host "`nInfo guardada en: cloudfront-deployment.json" -ForegroundColor Gray
    
} else {
    Write-Host "`n[ERROR] Error creando CloudFront:" -ForegroundColor Red
    Write-Host $result -ForegroundColor Yellow
}

Remove-Item "cloudfront-config.json" -ErrorAction SilentlyContinue
