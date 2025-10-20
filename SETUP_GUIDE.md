# 📘 Complete Setup Guide - AI DJ on Windows

This guide will take you step-by-step from scratch to having your AI DJ application automatically deployed on AWS.

## 📑 Table of Contents

1. [Base Software Installation](#1-base-software-installation)
2. [AWS Configuration](#2-aws-configuration)
3. [Spotify Configuration](#3-spotify-configuration)
4. [Local Project Configuration](#4-local-project-configuration)
5. [GitHub Configuration](#5-github-configuration)
6. [First Deployment](#6-first-deployment)
7. [Verification](#7-verification)

---

## 1. Base Software Installation

### 1.1 Python 3.12

1. Download Python from: https://www.python.org/downloads/
2. Run the installer
3. **IMPORTANT**: Check the "Add Python to PATH" box
4. Click "Install Now"
5. Verify the installation:
   ```powershell
   python --version
   # Should show: Python 3.12.x
   ```

### 1.2 Node.js 20

1. Download Node.js from: https://nodejs.org/
2. Run the installer (use default options)
3. Verify the installation:
   ```powershell
   node --version
   # Should show: v20.x.x
   
   npm --version
   # Should show: 10.x.x
   ```

### 1.3 AWS CLI

1. Download AWS CLI v2 from: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Run the installer
3. Verify the installation:
   ```powershell
   aws --version
   # Should show: aws-cli/2.x.x
   ```

### 1.4 Git

1. Download Git from: https://git-scm.com/download/win
2. Run the installer (use default options)
3. Verify the installation:
   ```powershell
   git --version
   # Should show: git version 2.x.x
   ```

### 1.5 AWS CDK

```powershell
# Install globally
npm install -g aws-cdk

# Verify installation
cdk --version
# Should show: 2.x.x
```

---

## 2. AWS Configuration

### 2.1 Create an AWS Account

1. Go to: https://aws.amazon.com/
2. Click "Create an AWS Account"
3. Complete the registration process (you will need a credit card)
4. Note your **Account ID** (12 digits) - you will find it in the top right corner

### 2.2 Create IAM User for Development

1. Go to the IAM console: https://console.aws.amazon.com/iam/
2. In the side menu, click "Users" → "Create user"
3. Username: `ai-dj-developer`
4. Check "Provide user access to the AWS Management Console" (optional)
5. Click "Next"
6. Select "Attach policies directly"
7. Search for and check: `AdministratorAccess` (for development)
8. Click "Next" → "Create user"

### 2.3 Create Access Keys

1. Click on the newly created user
2. Go to the "Security credentials" tab
3. Under "Access keys", click "Create access key"
4. Select "Command Line Interface (CLI)"
5. Check the confirmation and click "Next"
6. Add a description (optional) and click "Create access key"
7. **IMPORTANT**: Download the CSV file or copy the credentials:
   - Access key ID
   - Secret access key
8. Save them in a safe place (do not share them)

### 2.4 Configure AWS CLI

```powershell
aws configure
```

Enter:
- **AWS Access Key ID**: [Your Access Key ID]
- **AWS Secret Access Key**: [Your Secret Access Key]
- **Default region name**: `us-east-1`
- **Default output format**: `json`

Verify:
```powershell
aws sts get-caller-identity
# Should show your Account ID and User ARN
```

### 2.5 Enable Amazon Bedrock

1. Go to: https://console.aws.amazon.com/bedrock/
2. Make sure you are in the **us-east-1** region (top right corner)
3. In the side menu, click "Model access"
4. Click "Manage model access" (orange button)
5. Search for **Anthropic** and check:
   - ✅ Claude 3 Sonnet
6. Click "Request model access"
7. Wait a few seconds (usually approved instantly)
8. Verify that the status is "Access granted" (green)

---

## 3. Spotify Configuration

### 3.1 Create a Spotify Developer Account

1. Go to: https://developer.spotify.com/dashboard
2. Log in with your Spotify account (or create one)
3. Accept the terms of service

### 3.2 Create an Application

1. Click "Create app"
2. Complete the form:
   - **App name**: `AI DJ`
   - **App description**: `AI-powered playlist generator`
   - **Redirect URIs**: `http://localhost:8888/callback`
   - **Which API/SDKs are you planning to use?**: Check "Web API"
3. Accept the terms and click "Save"

### 3.3 Get Credentials

1. In your app's dashboard, click "Settings"
2. You will see:
   - **Client ID**: Copy it
   - **Client Secret**: Click "View client secret" and copy it
3. Save both values in a safe place

---

## 4. Local Project Configuration

### 4.1 Clone the Repository

```powershell
# Navigate to your projects folder
cd c:\dev\workspaces\hackaton

# If the project already exists
cd ai-dj

# If you need to clone it from GitHub
git clone https://github.com/YOUR_USER/ai-dj.git
cd ai-dj
```

### 4.2 Create Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

**If you get a permissions error**:
```powershell
# Run this first (as administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try to activate again
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the beginning of your prompt.

### 4.3 Install Dependencies

```powershell
# Make sure the virtual environment is activated
# You should see (.venv) in the prompt

# Upgrade pip
python -m pip install --upgrade pip

# Install CDK project dependencies
pip install -r requirements.txt

# Install Lambda dependencies
cd lambda_src
pip install -r requirements.txt
cd ..
```

### 4.4 Verify Project Structure

```powershell
# View structure
tree /F /A
```

You should see:
```
ai-dj/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── ai_dj/
│   ├── __init__.py
│   └── ai_dj_stack.py
├── lambda_src/
│   ├── __init__.py
│   ├── app.py
│   └── requirements.txt
├── app.py
├── cdk.json
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 5. GitHub Configuration

### 5.1 Create Repository on GitHub

1. Go to: https://github.com/new
2. Repository name: `ai-dj`
3. Description: `AI-powered Spotify playlist generator`
4. Select "Private" or "Public" as you prefer
5. **DO NOT** check "Initialize this repository with a README"
6. Click "Create repository"

### 5.2 Connect Local Repository

```powershell
# If it's a new repository
git init
git add .
git commit -m "Initial commit: AI DJ serverless app"
git branch -M main
git remote add origin https://github.com/YOUR_USER/ai-dj.git
git push -u origin main
```

### 5.3 Configure Secrets in GitHub

1. Go to your repository on GitHub
2. Click **Settings** (top tab)
3. In the side menu, go to **Secrets and variables** → **Actions**
4. Click **New repository secret**

Add the following secrets one by one:

#### Secret 1: AWS_ACCESS_KEY_ID
- **Name**: `AWS_ACCESS_KEY_ID`
- **Secret**: [Your AWS Access Key ID from step 2.3]
- Click "Add secret"

#### Secret 2: AWS_SECRET_ACCESS_KEY
- **Name**: `AWS_SECRET_ACCESS_KEY`
- **Secret**: [Your AWS Secret Access Key from step 2.3]
- Click "Add secret"

#### Secret 3: AWS_ACCOUNT_ID
- **Name**: `AWS_ACCOUNT_ID`
- **Secret**: [Your 12-digit AWS Account ID]
- Click "Add secret"

#### Secret 4: SPOTIFY_CLIENT_ID
- **Name**: `SPOTIFY_CLIENT_ID`
- **Secret**: [Your Spotify Client ID from step 3.3]
- Click "Add secret"

#### Secret 5: SPOTIFY_CLIENT_SECRET
- **Name**: `SPOTIFY_CLIENT_SECRET`
- **Secret**: [Your Spotify Client Secret from step 3.3]
- Click "Add secret"

### 5.4 Verify Secrets

You should see 5 secrets listed:
- ✅ AWS_ACCESS_KEY_ID
- ✅ AWS_SECRET_ACCESS_KEY
- ✅ AWS_ACCOUNT_ID
- ✅ SPOTIFY_CLIENT_ID
- ✅ SPOTIFY_CLIENT_SECRET

---

## 6. First Deployment

### 6.1 Option A: Automatic Deployment (Recommended)

```powershell
# Make sure all changes are committed
git status

# If there are pending changes
git add .
git commit -m "Ready for first deployment"

# Push to main to trigger deployment
git push origin main
```

### 6.2 Monitor the Deployment

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You will see the "Deploy AI DJ to AWS" workflow running
4. Click on the workflow to see the details
5. Expand each step to see the logs

**Estimated time**: 5-10 minutes

### 6.3 Option B: Local Deployment (Optional)

If you prefer to deploy from your machine:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Configure environment variables
$env:SPOTIFY_CLIENT_ID = "your_client_id_here"
$env:SPOTIFY_CLIENT_SECRET = "your_client_secret_here"

# Bootstrap (first time only)
cdk bootstrap

# Synthesize (check for errors)
cdk synth

# Deploy
cdk deploy

# Confirm with 'y' when prompted
```

---

## 7. Verification

### 7.1 Verify Successful Deployment

In GitHub Actions, the last step should show:

```
=== Deployment Outputs ===
{
  "AiDjStack": {
    "ApiEndpoint": "https://abc123xyz.execute-api.us-east-1.amazonaws.com/",
    "DynamoDBTableName": "AI-DJ-Users",
    "LambdaFunctionName": "AI-DJ-Handler"
  }
}
```

### 7.2 Get the API Endpoint

**From GitHub Actions**:
1. Go to the last successful workflow
2. Expand the "Display deployment outputs" step
3. Copy the `ApiEndpoint` value

**From AWS Console**:
1. Go to: https://console.aws.amazon.com/apigateway/
2. Look for "AI-DJ-API"
3. Copy the endpoint URL

**From command line**:
```powershell
aws cloudformation describe-stacks --stack-name AiDjStack --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" --output text
```

### 7.3 Test the API (Basic)

```powershell
# Save the endpoint to a variable
$API_ENDPOINT = "https://your-endpoint-here.execute-api.us-east-1.amazonaws.com"

# Test with curl (requires a valid Spotify access token)
curl -X POST "$API_ENDPOINT/playlist" `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": "test_user",
    "prompt": "Relaxing music for studying",
    "spotify_access_token": "YOUR_TOKEN_HERE"
  }'
```

**Note**: To get a Spotify access token, you need to implement OAuth 2.0. See Spotify documentation.

### 7.4 Verify Resources in AWS

**Lambda**:
```powershell
aws lambda get-function --function-name AI-DJ-Handler
```

**DynamoDB**:
```powershell
aws dynamodb describe-table --table-name AI-DJ-Users
```

**API Gateway**:
```powershell
aws apigatewayv2 get-apis
```

### 7.5 View Lambda Logs

```powershell
# View logs in real-time
aws logs tail /aws/lambda/AI-DJ-Handler --follow

# View recent logs
aws logs tail /aws/lambda/AI-DJ-Handler --since 1h
```

---

## 🎉 Congratulations!

Your AI DJ application is deployed and running. Now every time you push to `main`, it will be deployed automatically.

## 🔄 Next Steps

1. **Implement Spotify authentication**: Create an OAuth flow to get access tokens
2. **Create a frontend**: Web interface for users to interact with the API
3. **Add tests**: Unit and integration tests
4. **Monitoring**: Configure alarms in CloudWatch
5. **Optimization**: Adjust timeouts, memory, and costs

## 🆘 Common Troubleshooting

### Error: "Unable to locate credentials"
```powershell
# Reconfigure AWS CLI
aws configure
```

### Error: "Access Denied" in Bedrock
- Verify that you requested access to the model in the Bedrock console
- Make sure you are in the us-east-1 region

### Error: "Stack already exists"
```powershell
# Delete existing stack
cdk destroy
# Then deploy again
cdk deploy
```

### GitHub Actions fails at "CDK Bootstrap"
- Verify that secrets are configured correctly
- Make sure the IAM user has AdministratorAccess permissions

### Error: "Invalid client" on Spotify
- Verify that the Client ID and Client Secret are correct
- Make sure there are no extra spaces when copying/pasting

---

## 📞 Additional Resources

- **AWS CDK Docs**: https://docs.aws.amazon.com/cdk/
- **Spotify Web API**: https://developer.spotify.com/documentation/web-api
- **Amazon Bedrock**: https://docs.aws.amazon.com/bedrock/
- **GitHub Actions**: https://docs.github.com/en/actions

---

**Need help?** Open an issue in the GitHub repository.
