# Script para ver las solicitudes de acceso pendientes
Write-Host "🔍 Checking access requests in DynamoDB..." -ForegroundColor Cyan
Write-Host ""

# Get all access requests
$requests = aws dynamodb scan `
    --table-name AI-DJ-Users `
    --filter-expression "begins_with(user_id, :prefix)" `
    --expression-attribute-values '{":prefix":{"S":"ACCESS_REQUEST#"}}' `
    --output json | ConvertFrom-Json

if ($requests.Count -eq 0) {
    Write-Host "✅ No pending access requests" -ForegroundColor Green
    exit
}

Write-Host "📧 Pending Access Requests:" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow
Write-Host ""

foreach ($item in $requests.Items) {
    $email = $item.email.S
    $timestamp = $item.timestamp.S
    $status = $item.status.S
    
    Write-Host "Email: $email" -ForegroundColor White
    Write-Host "Date: $timestamp" -ForegroundColor Gray
    Write-Host "Status: $status" -ForegroundColor $(if ($status -eq "pending") { "Yellow" } else { "Green" })
    Write-Host "---" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "💡 To add a user to Spotify whitelist:" -ForegroundColor Cyan
Write-Host "1. Go to: https://developer.spotify.com/dashboard" -ForegroundColor White
Write-Host "2. Select 'AI DJ' app" -ForegroundColor White
Write-Host "3. Settings → User Management → Add User" -ForegroundColor White
Write-Host "4. Copy email from above and add it" -ForegroundColor White
