# Script to create hackathon submission ZIP
Write-Host "Creating AI DJ Hackathon Submission Package..." -ForegroundColor Green

# Create temporary submission folder
$submissionFolder = "ai-dj-submission"
if (Test-Path $submissionFolder) {
    Remove-Item -Recurse -Force $submissionFolder
}
New-Item -ItemType Directory -Force -Path $submissionFolder | Out-Null

Write-Host "Copying documentation files..." -ForegroundColor Yellow

# Copy main documentation
Copy-Item "README.md" "$submissionFolder/" -ErrorAction SilentlyContinue
Copy-Item "ARCHITECTURE.md" "$submissionFolder/" -ErrorAction SilentlyContinue
Copy-Item "HACKATHON_READY.md" "$submissionFolder/" -ErrorAction SilentlyContinue

Write-Host "Copying source code..." -ForegroundColor Yellow

# Copy source code
Copy-Item -Recurse "frontend" "$submissionFolder/" -ErrorAction SilentlyContinue
Copy-Item -Recurse "lambda_src" "$submissionFolder/" -ErrorAction SilentlyContinue
Copy-Item -Recurse "spotify_auth" "$submissionFolder/" -ErrorAction SilentlyContinue
Copy-Item -Recurse "ai_dj" "$submissionFolder/" -ErrorAction SilentlyContinue

# Copy important config files
Copy-Item "requirements.txt" "$submissionFolder/" -ErrorAction SilentlyContinue
Copy-Item "app.py" "$submissionFolder/" -ErrorAction SilentlyContinue
Copy-Item "cdk.json" "$submissionFolder/" -ErrorAction SilentlyContinue

Write-Host "Creating project info file..." -ForegroundColor Yellow

# Create a PROJECT_INFO.txt with key details
$projectInfo = @"
AI DJ - Intelligent Playlist Generator
=======================================

🌐 Live Demo: https://d1z4qoq01pmvv3.cloudfront.net
📦 GitHub: https://github.com/kaelen-phoenix/ai-dj

🏗️ Architecture:
- Frontend: HTML/CSS/JavaScript hosted on AWS S3 + CloudFront
- Backend: AWS Lambda (Python) + API Gateway
- AI: Amazon Bedrock (Claude 3 Sonnet)
- Database: DynamoDB
- Integration: Spotify Web API

✨ Key Features:
- Natural language playlist generation
- AI-powered music parameter extraction
- Real Spotify playlist creation
- Mobile-responsive design with app deep linking
- Serverless, scalable architecture

📚 Documentation:
- README.md: Setup and deployment instructions
- ARCHITECTURE.md: Technical architecture details
- HACKATHON_READY.md: Demo guide and talking points

🚀 Quick Start:
1. Deploy with AWS CDK: cdk deploy
2. Configure Spotify OAuth credentials
3. Access via CloudFront URL

Built with ❤️ using AWS, Bedrock AI, and Spotify API
"@

$projectInfo | Out-File -FilePath "$submissionFolder/PROJECT_INFO.txt" -Encoding UTF8

Write-Host "Creating ZIP file..." -ForegroundColor Yellow

# Create ZIP
$zipName = "ai-dj-hackathon-submission.zip"
if (Test-Path $zipName) {
    Remove-Item $zipName
}

Compress-Archive -Path "$submissionFolder/*" -DestinationPath $zipName

# Get file size
$fileSize = (Get-Item $zipName).Length / 1MB
$fileSizeMB = [math]::Round($fileSize, 2)

Write-Host "`n✅ Submission package created successfully!" -ForegroundColor Green
Write-Host "📦 File: $zipName" -ForegroundColor Cyan
Write-Host "📊 Size: $fileSizeMB MB (Limit: 35 MB)" -ForegroundColor Cyan

if ($fileSizeMB -gt 35) {
    Write-Host "⚠️  WARNING: File size exceeds 35 MB limit!" -ForegroundColor Red
} else {
    Write-Host "✅ File size is within limit" -ForegroundColor Green
}

# Clean up temporary folder
Write-Host "`nCleaning up..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $submissionFolder

Write-Host "`n🎉 Ready to submit!" -ForegroundColor Green
Write-Host "Upload the file: $zipName" -ForegroundColor Cyan
