# Ver logs recientes de la Lambda de Image Handler
Write-Host "Obteniendo logs de AI-DJ-Image-Handler..." -ForegroundColor Cyan

$logGroupName = "/aws/lambda/AI-DJ-Image-Handler"
$startTime = [DateTimeOffset]::UtcNow.AddMinutes(-10).ToUnixTimeMilliseconds()

Write-Host "Buscando logs desde hace 10 minutos..." -ForegroundColor Yellow

# Get recent log streams
$streams = aws logs describe-log-streams `
    --log-group-name $logGroupName `
    --order-by LastEventTime `
    --descending `
    --max-items 3 | ConvertFrom-Json

if ($streams.logStreams.Count -eq 0) {
    Write-Host "No se encontraron logs recientes" -ForegroundColor Red
    exit 1
}

Write-Host "Encontrados $($streams.logStreams.Count) streams recientes" -ForegroundColor Green

foreach ($stream in $streams.logStreams) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "Stream: $($stream.logStreamName)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    $events = aws logs get-log-events `
        --log-group-name $logGroupName `
        --log-stream-name $stream.logStreamName `
        --start-time $startTime `
        --limit 50 | ConvertFrom-Json
    
    foreach ($event in $events.events) {
        $timestamp = [DateTimeOffset]::FromUnixTimeMilliseconds($event.timestamp).LocalDateTime
        Write-Host "[$timestamp] $($event.message)"
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Logs completos" -ForegroundColor Green
