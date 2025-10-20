# Script para desplegar el frontend a AWS S3

Write-Host "Desplegando frontend de AI DJ a AWS..." -ForegroundColor Cyan

# Nombre del bucket (debe ser unico globalmente)
$bucketName = "ai-dj-frontend-$(Get-Random -Minimum 1000 -Maximum 9999)"

Write-Host "`n[1/5] Creando bucket S3..." -ForegroundColor Yellow
aws s3 mb s3://$bucketName --region us-east-1

Write-Host "`n[2/5] Configurando bucket para hosting web..." -ForegroundColor Yellow
aws s3 website s3://$bucketName --index-document index.html --error-document index.html

Write-Host "`n[3/5] Configurando politica publica..." -ForegroundColor Yellow
$policy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$bucketName/*"
        }
    ]
}
"@

$policy | Out-File -FilePath "bucket-policy.json" -Encoding UTF8
aws s3api put-bucket-policy --bucket $bucketName --policy file://bucket-policy.json
Remove-Item "bucket-policy.json"

Write-Host "`n[4/5] Subiendo archivos..." -ForegroundColor Yellow
aws s3 sync frontend/ s3://$bucketName/ --delete

Write-Host "`n[5/5] Configurando CORS..." -ForegroundColor Yellow
$cors = @"
{
    "CORSRules": [
        {
            "AllowedOrigins": ["*"],
            "AllowedMethods": ["GET", "HEAD"],
            "AllowedHeaders": ["*"],
            "MaxAgeSeconds": 3000
        }
    ]
}
"@

$cors | Out-File -FilePath "cors.json" -Encoding UTF8
aws s3api put-bucket-cors --bucket $bucketName --cors-configuration file://cors.json
Remove-Item "cors.json"

$websiteUrl = "http://$bucketName.s3-website-us-east-1.amazonaws.com"

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "[SUCCESS] Frontend desplegado!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "`nURL de tu aplicacion:" -ForegroundColor Cyan
Write-Host $websiteUrl -ForegroundColor White
Write-Host "`nBucket S3:" -ForegroundColor Cyan
Write-Host $bucketName -ForegroundColor White
Write-Host "`n============================================" -ForegroundColor Green
Write-Host "SIGUIENTE PASO:" -ForegroundColor Yellow
Write-Host "1. Ve a: https://developer.spotify.com/dashboard" -ForegroundColor White
Write-Host "2. Abre tu app 'AI DJ' > Settings" -ForegroundColor White
Write-Host "3. En 'Redirect URIs' agrega:" -ForegroundColor White
Write-Host "   $websiteUrl/" -ForegroundColor Cyan
Write-Host "4. Guarda los cambios" -ForegroundColor White
Write-Host "5. Abre tu app en: $websiteUrl" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green

# Guardar info
@{
    bucket = $bucketName
    url = $websiteUrl
} | ConvertTo-Json | Out-File -FilePath "frontend-deployment.json"

Write-Host "`nInfo guardada en: frontend-deployment.json" -ForegroundColor Gray
