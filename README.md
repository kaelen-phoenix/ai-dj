# 🎵 AI DJ - Intelligent Spotify Playlist Generator

AI DJ is a serverless application that uses artificial intelligence to create custom Spotify playlists based on natural language requests. It interprets the "vibe" you're looking for and automatically generates the perfect playlist for you.

## 🏗️ Architecture

- **AWS Lambda**: Processes requests and orchestrates the logic
- **Amazon Bedrock**: Interprets natural language using Claude 3 Sonnet
- **Amazon DynamoDB**: Stores user playlist history
- **Amazon API Gateway**: Exposes the REST API
- **Spotify Web API**: Searches for songs and creates playlists
- **AWS CDK**: Infrastructure as Code in Python
- **GitHub Actions**: Automatic CI/CD

## 📋 Prerequisites

### Required Software (Windows)

1. **Python 3.12+**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Node.js 20+**
   - Download from: https://nodejs.org/
   - Includes npm automatically

3. **AWS CLI v2**
   - Download from: https://aws.amazon.com/cli/
   - Verify installation: `aws --version`

4. **Git**
   - Download from: https://git-scm.com/download/win
   - Verify installation: `git --version`

5. **AWS CDK**
   ```powershell
   npm install -g aws-cdk
   cdk --version
   ```

### Required Accounts

1. **AWS Account**
   - Create at: https://aws.amazon.com/
   - You will need access to: Lambda, DynamoDB, API Gateway, Bedrock

2. **Spotify Developer Account**
   - Create at: https://developer.spotify.com/dashboard
   - Create an application to get a Client ID and Client Secret

3. **GitHub Account**
   - To host the code and run CI/CD

## 🚀 Local Environment Setup

### 1. Clone or Initialize the Repository

```powershell
# If you already have the code
cd c:\dev\workspaces\hackaton\ai-dj

# If starting from scratch
git init
git remote add origin https://github.com/YOUR_USER/ai-dj.git
```

### 2. Create Python Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# If you get a permissions error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Install Dependencies

```powershell
# CDK project dependencies
pip install -r requirements.txt

# Lambda dependencies (for local testing)
cd lambda_src
pip install -r requirements.txt
cd ..
```

### 4. Configure AWS CLI

```powershell
aws configure
```

Provide:
- **AWS Access Key ID**: Your access key
- **AWS Secret Access Key**: Your secret key
- **Default region name**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

### 5. Enable Amazon Bedrock

1. Go to the AWS Bedrock console: https://console.aws.amazon.com/bedrock/
2. Navigate to "Model access" in the side menu
3. Request access to the **Anthropic Claude 3 Sonnet** model
4. Wait for approval (usually instant)

### 6. Configure Spotify Developer App

1. Go to: https://developer.spotify.com/dashboard
2. Create a new application
3. Note the **Client ID** and **Client Secret**
4. In "Edit Settings", add Redirect URIs (for user authentication):
   - `http://localhost:8888/callback` (for development)
   - Your production URL when you have it

## 🔐 Configure Secrets in GitHub

For CI/CD to work, you need to configure the following secrets in your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add:

| Secret Name | Description | Where to Get It |
|-------------------|-------------|-----------------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID | AWS IAM Console |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | AWS IAM Console |
| `AWS_ACCOUNT_ID` | Your 12-digit AWS Account ID | AWS Console (top right corner) |
| `SPOTIFY_CLIENT_ID` | Spotify Client ID | Spotify Developer Dashboard |
| `SPOTIFY_CLIENT_SECRET` | Spotify Client Secret | Spotify Developer Dashboard |

### Create IAM User for GitHub Actions

```powershell
# Create user with necessary permissions
aws iam create-user --user-name github-actions-ai-dj

# Attach necessary policies
aws iam attach-user-policy --user-name github-actions-ai-dj --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create access key
aws iam create-access-key --user-name github-actions-ai-dj
```

**Note**: In production, use more restrictive permissions instead of `AdministratorAccess`.

## 🧪 Local Deployment (Optional)

To test deployment from your local machine:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Configure environment variables
$env:SPOTIFY_CLIENT_ID = "your_client_id"
$env:SPOTIFY_CLIENT_SECRET = "your_client_secret"

# CDK Bootstrap (first time only)
cdk bootstrap

# Synthesize the stack (check for errors)
cdk synth

# Deploy
cdk deploy

# View outputs (API endpoint, etc.)
cdk deploy --outputs-file outputs.json
```

## 🚢 Automatic Deployment with GitHub Actions

### First Time

1. **Make sure you have all secrets configured** (see previous section)

2. **Commit your code**:
   ```powershell
   git add .
   git commit -m "Initial commit: AI DJ serverless app"
   ```

3. **Push to the main branch**:
   ```powershell
   git push origin main
   ```

4. **Monitor the deployment**:
   - Go to your repository on GitHub
   - Navigate to the **Actions** tab
   - You will see the "Deploy AI DJ to AWS" workflow running
   - Click on the workflow to see the real-time logs

### Subsequent Deployments

Every time you `git push` to the `main` branch, it will be deployed automatically:

```powershell
# Make changes to the code
# ...

# Commit and push
git add .
git commit -m "Description of your changes"
git push origin main
```

## 📡 API Usage

Once deployed, you will get an API Gateway endpoint. Example:

```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/
```

### Endpoint: POST /playlist

**Request**:
```json
{
  "user_id": "user123",
  "prompt": "Energetic music for working out, some rock and electronic",
  "spotify_access_token": "BQD...user_token"
}
```

**Response**:
```json
{
  "message": "Playlist created successfully",
  "playlist_url": "https://open.spotify.com/playlist/abc123",
  "tracks_count": 20,
  "parameters": {
    "genres": ["rock", "electronic"],
    "mood": "energetic",
    "energy": 0.8,
    "danceability": 0.7,
    "valence": 0.6,
    "playlist_name": "AI DJ - Workout Mix"
  }
}
```

### Get Spotify Access Token

Users must authenticate with Spotify using OAuth 2.0. Basic example:

1. **Authorization Code Flow**: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
2. **Required scopes**: `playlist-modify-public`, `playlist-modify-private`

## 🧹 Resource Cleanup

To delete all AWS resources and avoid charges:

```powershell
# From your local machine
cdk destroy

# Confirm with 'y' when prompted
```

Or from GitHub Actions, you can create a manual destruction workflow.

## 📊 Monitoring and Logs

### View Lambda logs

```powershell
# Using AWS CLI
aws logs tail /aws/lambda/AI-DJ-Handler --follow

# Or from the AWS console
# CloudWatch → Log groups → /aws/lambda/AI-DJ-Handler
```

### View metrics

- **Lambda**: CloudWatch → Metrics → Lambda → By Function Name
- **API Gateway**: CloudWatch → Metrics → ApiGateway
- **DynamoDB**: CloudWatch → Metrics → DynamoDB → Table Metrics

## 🔧 Troubleshooting

### Error: "Unable to locate credentials"

```powershell
# Check AWS configuration
aws configure list

# Reconfigure if necessary
aws configure
```

### Error: "Access Denied" in Bedrock

- Verify that you have requested access to the Claude 3 Sonnet model in the Bedrock console
- Make sure you are in the correct region (us-east-1)

### Error: "Invalid client" on Spotify

- Verify that `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` are correct
- Make sure the environment variables are configured in GitHub Secrets

### GitHub Actions pipeline fails

- Verify that all secrets are configured correctly
- Review the workflow logs in the Actions tab
- Make sure the IAM user has the necessary permissions

## 📝 Project Structure

```
ai-dj/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD Pipeline
├── ai_dj/
│   ├── __init__.py
│   └── ai_dj_stack.py         # CDK infrastructure definition
├── lambda_src/
│   ├── __init__.py
│   ├── app.py                 # Lambda code
│   └── requirements.txt       # Lambda dependencies
├── app.py                     # CDK entry point
├── cdk.json                   # CDK configuration
├── requirements.txt           # CDK project dependencies
├── .gitignore
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the MIT license.

## 🎯 Next Steps

- [ ] Implement user authentication with Cognito
- [ ] Add a web frontend with React
- [ ] Support for multiple AI models
- [ ] More advanced sentiment analysis
- [ ] Integration with other music platforms
- [ ] Unit and integration tests
- [ ] API documentation with OpenAPI/Swagger

## 📞 Support

If you have problems or questions:
- Open an issue on GitHub
- Review the AWS CDK documentation: https://docs.aws.amazon.com/cdk/
- Consult the Spotify API: https://developer.spotify.com/documentation/web-api
- Bedrock Documentation: https://docs.aws.amazon.com/bedrock/

---

**Enjoy creating playlists with AI! 🎵🤖**
