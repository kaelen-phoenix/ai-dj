# 🏗️ AI DJ Architecture

## System Overview

AI DJ is a serverless application that creates personalized Spotify playlists using artificial intelligence.

```
User → CloudFront (Frontend) → API Gateway → Lambda → Bedrock (AI)
                                                    ↓
                                            Spotify API
                                                    ↓
                                              DynamoDB
```

## Components

### Frontend
- **Technology**: Static HTML/CSS/JavaScript
- **Hosting**: Amazon S3 + CloudFront (HTTPS)
- **Features**:
  - Spotify OAuth 2.0 authentication
  - Responsive design
  - Real-time playlist creation

### Backend

#### API Gateway
- **Type**: HTTP API
- **Endpoints**:
  - `POST /playlist` - Create playlist
  - `GET /callback` - OAuth callback
- **Features**: CORS enabled, automatic scaling

#### Lambda Functions

**1. Main Handler (`AI-DJ-Handler`)**
- **Runtime**: Python 3.12
- **Memory**: 512 MB
- **Timeout**: 60 seconds
- **Responsibilities**:
  - Receive user prompts
  - Call Bedrock for AI analysis
  - Search Spotify for tracks
  - Create playlists
  - Store history in DynamoDB

**2. OAuth Handler (`Spotify-OAuth-Handler`)**
- **Runtime**: Python 3.12
- **Memory**: 256 MB
- **Timeout**: 30 seconds
- **Responsibilities**:
  - Handle Spotify OAuth callback
  - Exchange authorization code for access token
  - Redirect to frontend with token

#### Amazon Bedrock
- **Model**: Claude 3 Sonnet
- **Purpose**: Interpret natural language prompts
- **Output**: Music parameters and search terms

#### DynamoDB
- **Table**: `AI-DJ-Users`
- **Schema**:
  - `user_id` (Partition Key)
  - `timestamp` (Sort Key)
  - `playlist_url`
  - `prompt`
  - `parameters`

#### Spotify Web API
- **Authentication**: OAuth 2.0 (Authorization Code Flow)
- **Endpoints Used**:
  - `/search` - Find tracks
  - `/users/{user_id}/playlists` - Create playlist
  - `/playlists/{playlist_id}/tracks` - Add tracks

## Data Flow

### 1. User Authentication
```
1. User clicks "Connect with Spotify"
2. Redirects to Spotify authorization
3. User authorizes application
4. Spotify redirects to /callback with code
5. Lambda exchanges code for access token
6. Lambda redirects to frontend with token in URL hash
7. Frontend saves token to localStorage
```

### 2. Playlist Creation
```
1. User enters prompt (e.g., "relaxing music for studying")
2. Frontend sends POST to /playlist with:
   - user_id
   - prompt
   - spotify_access_token
3. Lambda receives request
4. Lambda calls Bedrock with prompt
5. Bedrock analyzes and returns:
   - search_terms: ["lofi hip hop", "study beats", ...]
   - mood, energy, danceability, etc.
6. Lambda searches Spotify with each search term
7. Lambda combines and filters results
8. Lambda creates playlist in user's Spotify
9. Lambda saves to DynamoDB
10. Lambda returns playlist URL
11. Frontend displays success and link
```

## AI Intelligence

### Bedrock Prompt Engineering

The AI receives prompts like:
- "music for studying"
- "energetic workout music"
- "sad piano songs"

And generates intelligent search strategies:

**Example Input**: "música para relajarse estudiando"

**AI Output**:
```json
{
  "search_terms": [
    "lofi hip hop",
    "study beats",
    "ambient piano",
    "calm instrumental",
    "focus music"
  ],
  "mood": "chill",
  "energy": 0.3,
  "danceability": 0.3,
  "valence": 0.5,
  "playlist_name": "Study & Relax"
}
```

### Smart Search Strategy

1. **Priority 1**: AI-suggested search terms (best results)
2. **Priority 2**: Genre-based search
3. **Priority 3**: Mood keywords
4. **Priority 4**: Recent popular music (fallback)

The system searches Spotify with multiple queries, combines results, removes duplicates, and returns the best matches.

## Infrastructure as Code

### AWS CDK Stack

All infrastructure is defined in Python using AWS CDK:

```python
# Key resources
- Lambda Functions (with layers for dependencies)
- API Gateway HTTP API
- DynamoDB Table
- S3 Bucket (frontend)
- CloudFront Distribution (CDN)
- IAM Roles and Policies
```

### Deployment

Fully automated via GitHub Actions:
1. Push to `main` branch
2. GitHub Actions runs
3. CDK synthesizes CloudFormation
4. Deploys to AWS
5. Outputs API endpoint and frontend URL

## Security

### Authentication & Authorization
- Spotify OAuth 2.0 for user authentication
- User tokens never stored server-side
- Tokens passed in requests, validated by Spotify

### IAM Permissions
- Lambda execution roles with minimal permissions
- Bedrock invoke access
- DynamoDB read/write access
- No public database access

### HTTPS Everywhere
- CloudFront serves frontend over HTTPS
- API Gateway uses HTTPS
- All Spotify API calls use HTTPS

## Scalability

### Serverless Benefits
- **Auto-scaling**: Lambda scales automatically
- **No servers to manage**: Fully managed services
- **Pay per use**: Only pay for actual usage
- **Global CDN**: CloudFront edge locations worldwide

### Performance
- **Lambda cold start**: ~1-2 seconds
- **Warm execution**: ~2-3 seconds
- **Bedrock response**: ~1-2 seconds
- **Total time**: ~3-5 seconds per playlist

## Monitoring

### CloudWatch Logs
- Lambda function logs
- API Gateway access logs
- Error tracking and debugging

### Metrics
- Request count
- Error rate
- Execution duration
- DynamoDB read/write units

## Cost Estimation

### AWS Free Tier (12 months)
- Lambda: 1M requests/month
- DynamoDB: 25 GB storage
- CloudFront: 1 TB data transfer
- API Gateway: 1M requests/month

### After Free Tier (estimated for 1000 playlists/month)
- Lambda: ~$0.20
- DynamoDB: ~$0.25
- API Gateway: ~$0.01
- CloudFront: ~$0.10
- Bedrock: ~$3.00 (Claude 3 Sonnet)
- **Total**: ~$3.56/month

## Technology Stack

### Backend
- **Language**: Python 3.12
- **Framework**: AWS Lambda
- **AI**: Amazon Bedrock (Claude 3 Sonnet)
- **Database**: Amazon DynamoDB
- **API**: Amazon API Gateway

### Frontend
- **Language**: JavaScript (Vanilla)
- **Hosting**: Amazon S3 + CloudFront
- **Styling**: CSS3
- **Authentication**: Spotify OAuth 2.0

### Infrastructure
- **IaC**: AWS CDK (Python)
- **CI/CD**: GitHub Actions
- **Version Control**: Git

### External APIs
- **Spotify Web API**: Music search and playlist creation
- **Amazon Bedrock**: AI-powered prompt interpretation

## Future Enhancements

- [ ] User authentication with AWS Cognito
- [ ] Playlist history and favorites
- [ ] Share playlists with friends
- [ ] Advanced filters (tempo, key, etc.)
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Analytics dashboard
- [ ] Playlist recommendations

---

**Built with ❤️ using AWS Serverless Technologies**
