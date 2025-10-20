# 🏗️ AI DJ Architecture

## Architecture Diagram

```
┌───────────┐
│   User    │
└─────┬─────┘
      │ HTTP POST /playlist
      │ {user_id, prompt, spotify_access_token}
      ▼
┌─────────────────────────────────────────┐
│     Amazon API Gateway (HTTP API)       │
│  - CORS enabled                         │
│  - Route: POST /playlist                │
└──────────────┬──────────────────────────┘
               │ Invokes
               ▼
┌─────────────────────────────────────────┐
│         AWS Lambda Function             │
│  - Runtime: Python 3.12                 │
│  - Timeout: 60s                         │
│  - Memory: 512 MB                       │
│  - Handler: app.lambda_handler          │
└──┬────────┬────────┬────────────────────┘
   │        │        │
   │        │        └──────────────────┐
   │        │                           │
   │        │ Invokes model             │ Read/Write
   │        ▼                           ▼
   │  ┌──────────────────┐    ┌──────────────────┐
   │  │ Amazon Bedrock   │    │ Amazon DynamoDB  │
   │  │ Claude 3 Sonnet  │    │ Table: AI-DJ-    │
   │  │                  │    │ Users            │
   │  │ Interprets       │    │ PK: user_id      │
   │  │ natural language │    │                  │
   │  │ → musical        │    │ Stores:          │
   │  │   parameters     │    │ - History        │
   │  └──────────────────┘    │ - Playlists      │
   │                          └──────────────────┘
   │
   │ Searches for songs and creates playlist
   ▼
┌─────────────────────────────────────────┐
│         Spotify Web API                 │
│  - Search tracks                        │
│  - Get audio features                   │
│  - Create playlist                      │
│  - Add tracks to playlist               │
└─────────────────────────────────────────┘
```

## Detailed Data Flow

### 1. Request Reception

```
User → API Gateway → Lambda
```

**Input Payload**:
```json
{
  "user_id": "user123",
  "prompt": "Energetic music for working out",
  "spotify_access_token": "BQD...token"
}
```

### 2. AI Interpretation

```
Lambda → Bedrock (Claude 3 Sonnet)
```

**Prompt to the model**:
```
System: You are a music expert who interprets user requests...
User: Create a playlist based on: Energetic music for working out
```

**Model Response**:
```json
{
  "genres": ["rock", "electronic", "pop"],
  "mood": "energetic",
  "energy": 0.85,
  "danceability": 0.75,
  "valence": 0.7,
  "tempo": 140,
  "popularity": 60,
  "playlist_name": "AI DJ - Workout Energy",
  "limit": 20
}
```

### 3. Song Search

```
Lambda → Spotify API (Search)
```

**Request**:
```
GET /v1/search?q=genre:"rock" OR genre:"electronic"&type=track&limit=50
Authorization: Bearer {spotify_access_token}
```

**Response**: List of 50 candidate songs

### 4. Filtering by Audio Features

```
Lambda → Spotify API (Audio Features)
```

**Request**:
```
GET /v1/audio-features?ids=track1,track2,...,track50
Authorization: Bearer {spotify_access_token}
```

**Response**: Audio features for each song

**Filtering algorithm**:
```python
for track, features in zip(tracks, audio_features):
    energy_diff = abs(features['energy'] - target_energy)
    dance_diff = abs(features['danceability'] - target_danceability)
    valence_diff = abs(features['valence'] - target_valence)
    
    score = 1 - (energy_diff + dance_diff + valence_diff) / 3
    
    if track['popularity'] >= min_popularity:
        filtered_tracks.append({'track': track, 'score': score})

# Sort by score and take the best ones
filtered_tracks.sort(key=lambda x: x['score'], reverse=True)
best_tracks = filtered_tracks[:limit]
```

### 5. Playlist Creation

```
Lambda → Spotify API (Create Playlist)
```

**Request 1**: Get Spotify User ID
```
GET /v1/me
Authorization: Bearer {spotify_access_token}
```

**Request 2**: Create playlist
```
POST /v1/users/{user_id}/playlists
{
  "name": "AI DJ - Workout Energy",
  "description": "Created by AI DJ - 2025-10-10 03:48 UTC",
  "public": true
}
```

**Request 3**: Add songs
```
POST /v1/playlists/{playlist_id}/tracks
{
  "uris": ["spotify:track:abc123", "spotify:track:def456", ...]
}
```

### 6. Storage in DynamoDB

```
Lambda → DynamoDB
```

**Operation**: PutItem

**Item**:
```json
{
  "user_id": "user123",
  "playlists": [
    {
      "playlist_url": "https://open.spotify.com/playlist/xyz789",
      "prompt": "Energetic music for working out",
      "parameters": {
        "genres": ["rock", "electronic"],
        "mood": "energetic",
        "energy": 0.85
      },
      "created_at": "2025-10-10T03:48:00.000Z"
    }
  ],
  "last_updated": "2025-10-10T03:48:00.000Z"
}
```

### 7. Response to the User

```
Lambda → API Gateway → User
```

**Response**:
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": {
    "message": "Playlist created successfully",
    "playlist_url": "https://open.spotify.com/playlist/xyz789",
    "tracks_count": 20,
    "parameters": {
      "genres": ["rock", "electronic"],
      "mood": "energetic",
      "energy": 0.85,
      "danceability": 0.75,
      "valence": 0.7
    }
  }
}
```

## AWS Components

### AWS Lambda

**Configuration**:
- **Runtime**: Python 3.12
- **Handler**: `app.lambda_handler`
- **Timeout**: 60 seconds
- **Memory**: 512 MB
- **Concurrency**: No limit (default)

**Environment variables**:
- `SPOTIFY_CLIENT_ID`: Spotify client ID
- `SPOTIFY_CLIENT_SECRET`: Spotify client secret
- `DYNAMODB_TABLE_NAME`: DynamoDB table name
- `BEDROCK_MODEL_ID`: Bedrock model ID
- `AWS_REGION`: AWS region (automatic)

**IAM Permissions**:
- `dynamodb:GetItem`
- `dynamodb:PutItem`
- `bedrock:InvokeModel`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

### Amazon API Gateway

**Type**: HTTP API (cheaper and simpler than REST API)

**Configuration**:
- **CORS**: Enabled for all origins
- **Allowed methods**: POST, OPTIONS
- **Allowed headers**: Content-Type, Authorization

**Routes**:
- `POST /playlist` → Lambda Integration

**Throttling**: No custom limits (uses AWS defaults)

### Amazon DynamoDB

**Configuration**:
- **Name**: AI-DJ-Users
- **Partition Key**: `user_id` (String)
- **Billing Mode**: Pay-per-request (on-demand)
- **Point-in-time recovery**: Enabled

**Data structure**:
```
{
  "user_id": "String (PK)",
  "playlists": [
    {
      "playlist_url": "String",
      "prompt": "String",
      "parameters": {
        "genres": ["String"],
        "mood": "String",
        "energy": Number,
        ...
      },
      "created_at": "String (ISO 8601)"
    }
  ],
  "last_updated": "String (ISO 8601)"
}
```

**Access patterns**:
1. Get a user's history: `GetItem(user_id)`
2. Save a new playlist: `PutItem(user_id, playlists)`

### Amazon Bedrock

**Model**: `anthropic.claude-3-sonnet-20240229-v1:0`

**Features**:
- **Context**: 200K tokens
- **Max output**: 4K tokens
- **Multimodal**: Yes (text and images)
- **Speed**: ~50 tokens/second

**Usage in AI DJ**:
- Natural language interpretation
- Extraction of musical parameters
- Generation of playlist names

**Estimated cost**:
- Input: $0.003 / 1K tokens
- Output: $0.015 / 1K tokens
- ~$0.02 per request

## Infrastructure as Code (CDK)

### Main Stack: `AiDjStack`

**Created resources**:
1. DynamoDB Table
2. Lambda Function
3. IAM Role (for Lambda)
4. IAM Policies (permissions)
5. API Gateway HTTP API
6. Lambda Integration
7. CloudWatch Log Groups (automatic)

**Outputs**:
- `ApiEndpoint`: API Gateway URL
- `DynamoDBTableName`: Table name
- `LambdaFunctionName`: Function name

### Dependencies

**CDK (requirements.txt)**:
```
aws-cdk-lib==2.149.0
constructs>=10.0.0,<11.0.0
```

**Lambda (lambda_src/requirements.txt)**:
```
boto3>=1.34.0
requests>=2.31.0
```

## CI/CD with GitHub Actions

### Workflow: `deploy.yml`

**Triggers**:
- Push to `main` branch
- Manual (workflow_dispatch)

**Jobs**:
1. **Checkout**: Clone code
2. **Configure AWS**: Authenticate with AWS
3. **Setup Node.js**: Install Node.js 20
4. **Install CDK**: Install AWS CDK CLI
5. **Setup Python**: Install Python 3.12
6. **Install Dependencies**: Install CDK and Lambda dependencies
7. **CDK Synth**: Synthesize CloudFormation
8. **CDK Bootstrap**: Prepare environment (first time only)
9. **CDK Deploy**: Deploy stack
10. **Display Outputs**: Show results
11. **Upload Artifacts**: Save outputs.json

**Required secrets**:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`

## Security

### Authentication and Authorization

**API Gateway**:
- No authentication (public)
- CORS configured
- Default AWS rate limiting

**Spotify**:
- OAuth 2.0
- User access token required
- Scopes: `playlist-modify-public`, `playlist-modify-private`

**AWS**:
- IAM roles with least privilege
- Credentials in GitHub Secrets
- No hardcoded credentials

### Sensitive Data

**Environment variables**:
- Encrypted in Lambda
- Injected at deployment time
- Not exposed in logs

**DynamoDB**:
- Encryption at rest (default)
- Encryption in transit (HTTPS)
- Automatic backups with PITR

### Implemented Best Practices

1. ✅ Principle of least privilege (IAM)
2. ✅ Secrets in environment variables
3. ✅ HTTPS in all communications
4. ✅ Input validation
5. ✅ Error handling
6. ✅ Structured logging
7. ✅ Data encryption

## Scalability

### Limits and Capacity

**Lambda**:
- **Concurrency**: 1000 concurrent executions (default)
- **Scaling**: Automatic
- **Cold start**: ~1-2 seconds

**API Gateway**:
- **Requests**: 10,000 RPS (default)
- **Throttling**: Configurable

**DynamoDB**:
- **Capacity**: Unlimited (on-demand)
- **Throughput**: Automatic
- **Latency**: <10ms (p99)

**Bedrock**:
- **Throttling**: 200 requests/minute (default)
- **Tokens**: 200K input, 4K output

### Potential Optimizations

1. **Lambda**:
   - Provisioned concurrency to eliminate cold starts
   - Increase memory for more CPU
   - Reuse HTTP connections

2. **DynamoDB**:
   - DAX (cache) for frequent reads
   - Global tables for multi-region
   - Secondary indexes for complex queries

3. **API Gateway**:
   - Response caching
   - API Keys for per-user rate limiting
   - WAF for DDoS protection

4. **Bedrock**:
   - Caching of common responses
   - Batch processing
   - Smaller model (Haiku) for simple cases

## Estimated Costs

### Per Request

- **Lambda**: $0.0000002 (200ms @ 512MB)
- **API Gateway**: $0.000001
- **DynamoDB**: $0.00000125 (1 write + 1 read)
- **Bedrock**: $0.02 (average)
- **Spotify API**: Free
- **Total**: ~$0.021 per created playlist

### Monthly (1000 playlists)

- **Lambda**: $0.20
- **API Gateway**: $1.00
- **DynamoDB**: $1.25
- **Bedrock**: $20.00
- **Total**: ~$22.45/month

### Free Tier (first year)

- **Lambda**: 1M requests/month free
- **API Gateway**: 1M requests/month free
- **DynamoDB**: 25GB storage + 25 WCU/RCU free
- **Bedrock**: No free tier

## Monitoring and Observability

### CloudWatch Metrics

**Lambda**:
- Invocations
- Duration
- Errors
- Throttles
- Concurrent executions

**API Gateway**:
- Count (requests)
- 4XXError
- 5XXError
- Latency
- IntegrationLatency

**DynamoDB**:
- ConsumedReadCapacityUnits
- ConsumedWriteCapacityUnits
- UserErrors
- SystemErrors

### CloudWatch Logs

**Lambda logs**:
```
/aws/lambda/AI-DJ-Handler
```

**Structured logs**:
```python
print(f"Processing request for user_id: {user_id}")
print(f"Extracted music parameters: {music_parameters}")
print(f"Found {len(tracks)} tracks")
print(f"Created playlist: {playlist_url}")
```

### Recommended Alarms

1. **Lambda Errors > 5% in 5 minutes**
2. **API Gateway 5XX > 1% in 5 minutes**
3. **Lambda Duration > 50 seconds**
4. **DynamoDB Throttled Requests > 0**

## Testing

### Local Tests

**Lambda**:
```python
# test_lambda.py
from lambda_src.app import lambda_handler

event = {
    'body': json.dumps({
        'user_id': 'test',
        'prompt': 'happy music',
        'spotify_access_token': 'token'
    })
}

response = lambda_handler(event, None)
print(response)
```

**CDK**:
```powershell
cdk synth
cdk diff
```

### Integration Tests

```powershell
# Deploy to test environment
cdk deploy --context env=test

# Run tests
pytest tests/integration/

# Clean up
cdk destroy --context env=test
```

## Improvement Roadmap

### Short Term
- [ ] User authentication (Cognito)
- [ ] Per-user rate limiting
- [ ] Bedrock results caching
- [ ] Unit tests

### Medium Term
- [ ] Web frontend (React)
- [ ] Multiple AI models
- [ ] Advanced sentiment analysis
- [ ] Usage metrics

### Long Term
- [ ] Multi-region
- [ ] Integration with other platforms (Apple Music, YouTube Music)
- [ ] Personalized recommendations
- [ ] Public API with OpenAPI documentation

---

**Last updated**: 2025-10-10
