# ⚡ Quick Start - AI DJ

A quick guide for experienced developers who want to deploy AI DJ in less than 15 minutes.

## Prerequisites

- ✅ Python 3.12+
- ✅ Node.js 20+
- ✅ AWS CLI configured
- ✅ AWS account with Bedrock access
- ✅ Spotify Developer App (Client ID + Secret)
- ✅ GitHub account

## Quick Install (Windows)

### 1. Install Tools

```powershell
# Python
winget install Python.Python.3.12

# Node.js
winget install OpenJS.NodeJS

# AWS CLI
winget install Amazon.AWSCLI

# Git
winget install Git.Git

# AWS CDK
npm install -g aws-cdk
```

### 2. Configure AWS

```powershell
# Configure credentials
aws configure
# AWS Access Key ID: [your_key]
# AWS Secret Access Key: [your_secret]
# Default region: us-east-1
# Default output: json

# Enable Bedrock Claude 3 Sonnet
# Go to: https://console.aws.amazon.com/bedrock/
# Model access → Request access → Anthropic Claude 3 Sonnet
```

### 3. Clone and Configure Project

```powershell
# Clone
cd c:\dev\workspaces\hackaton
git clone https://github.com/YOUR_USER/ai-dj.git
cd ai-dj

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
cd lambda_src
pip install -r requirements.txt
cd ..
```

### 4. Deploy

```powershell
# Configure environment variables
$env:SPOTIFY_CLIENT_ID = "your_spotify_client_id"
$env:SPOTIFY_CLIENT_SECRET = "your_spotify_client_secret"

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy
cdk deploy

# Copy the API Endpoint from the output
```

### 5. Configure GitHub Actions

1. Push the code to GitHub:
   ```powershell
   git remote add origin https://github.com/YOUR_USER/ai-dj.git
   git branch -M main
   git push -u origin main
   ```

2. Configure secrets in GitHub (Settings → Secrets → Actions):
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_ACCOUNT_ID`
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`

3. The next push will deploy automatically:
   ```powershell
   git add .
   git commit -m "Update"
   git push
   ```

## Test the API

```powershell
# Save endpoint
$API = "https://your-endpoint.execute-api.us-east-1.amazonaws.com"

# Call API (you need a valid Spotify access token)
$body = @{
    user_id = "test_user"
    prompt = "Energetic music for working out"
    spotify_access_token = "YOUR_SPOTIFY_TOKEN"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$API/playlist" -Method Post -Body $body -ContentType "application/json"
```

## Project Structure

```
ai-dj/
├── .github/workflows/deploy.yml    # CI/CD
├── ai_dj/
│   └── ai_dj_stack.py             # CDK Infrastructure
├── lambda_src/
│   ├── app.py                     # Lambda handler
│   └── requirements.txt           # Lambda dependencies
├── app.py                         # CDK entry point
├── cdk.json                       # CDK config
└── requirements.txt               # CDK dependencies
```

## Useful Commands

```powershell
# Synthesize CloudFormation
cdk synth

# See differences before deploying
cdk diff

# Deploy
cdk deploy

# View Lambda logs
aws logs tail /aws/lambda/AI-DJ-Handler --follow

# Destroy stack
cdk destroy
```

## Created AWS Resources

- **Lambda Function**: `AI-DJ-Handler`
- **DynamoDB Table**: `AI-DJ-Users`
- **API Gateway**: `AI-DJ-API`
- **IAM Role**: For Lambda with DynamoDB and Bedrock permissions
- **CloudWatch Log Group**: `/aws/lambda/AI-DJ-Handler`

## Estimated Costs

- **Lambda**: ~$0.20/month (1000 invocations)
- **API Gateway**: ~$1.00/month (1000 requests)
- **DynamoDB**: ~$1.25/month (on-demand)
- **Bedrock**: ~$20.00/month (1000 requests)
- **Total**: ~$22.45/month

## Troubleshooting

### Error: "Unable to locate credentials"
```powershell
aws configure
```

### Error: "Access Denied" in Bedrock
- Enable Claude 3 Sonnet in the Bedrock console (us-east-1)

### Error: "Invalid client" on Spotify
- Check Client ID and Secret in Spotify Developer Dashboard

### GitHub Actions fails
- Check that all secrets are configured
- Review the logs in the Actions tab

## Next Steps

1. **Implement Spotify authentication**: See `SPOTIFY_AUTH_GUIDE.md`
2. **Create a frontend**: React + TailwindCSS
3. **Add tests**: pytest + moto
4. **Configure alarms**: CloudWatch Alarms

## Full Documentation

- **Detailed Setup**: `SETUP_GUIDE.md`
- **Architecture**: `ARCHITECTURE.md`
- **API Reference**: `API_DOCUMENTATION.md`
- **Spotify OAuth**: `SPOTIFY_AUTH_GUIDE.md`

## Support

- GitHub Issues: https://github.com/YOUR_USER/ai-dj/issues
- AWS CDK Docs: https://docs.aws.amazon.com/cdk/
- Spotify API: https://developer.spotify.com/documentation/

---

**Ready to create playlists with AI! 🎵🤖**
