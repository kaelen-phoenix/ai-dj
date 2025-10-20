# Probar que Bedrock funciona
Write-Host "Probando Amazon Bedrock..." -ForegroundColor Cyan

$modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

$payload = @{
    anthropic_version = "bedrock-2023-05-31"
    max_tokens = 100
    messages = @(
        @{
            role = "user"
            content = "Di 'Hola, Bedrock funciona!' en una sola linea"
        }
    )
} | ConvertTo-Json -Depth 10

# Guardar payload en archivo temporal
$payload | Out-File -FilePath "bedrock-test-payload.json" -Encoding UTF8

Write-Host "Invocando modelo Claude 3 Sonnet..." -ForegroundColor Yellow

try {
    aws bedrock-runtime invoke-model `
        --model-id $modelId `
        --body file://bedrock-test-payload.json `
        --region us-east-1 `
        bedrock-response.json
    
    Write-Host "`n[SUCCESS] Bedrock respondio!" -ForegroundColor Green
    
    $response = Get-Content "bedrock-response.json" | ConvertFrom-Json
    $text = $response.content[0].text
    
    Write-Host "`nRespuesta de Claude:" -ForegroundColor Cyan
    Write-Host $text -ForegroundColor White
    
    # Limpiar archivos temporales
    Remove-Item "bedrock-test-payload.json" -ErrorAction SilentlyContinue
    Remove-Item "bedrock-response.json" -ErrorAction SilentlyContinue
    
    Write-Host "`n[OK] Bedrock esta funcionando correctamente!" -ForegroundColor Green
    
} catch {
    Write-Host "`n[ERROR] Error al invocar Bedrock:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Yellow
    
    if ($_.Exception.Message -like "*ResourceNotFoundException*") {
        Write-Host "`n[INFO] Necesitas activar Claude en el Playground primero:" -ForegroundColor Cyan
        Write-Host "https://console.aws.amazon.com/bedrock/home?region=us-east-1#/playground" -ForegroundColor White
    }
}
