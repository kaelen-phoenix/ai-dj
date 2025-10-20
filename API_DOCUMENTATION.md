# 📡 API Documentation - AI DJ

## Base URL

```
https://{api-id}.execute-api.{region}.amazonaws.com/
```

Example:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/
```

## Authentication

The API does not require authentication at the API Gateway level, but **it does require a valid Spotify Access Token** in the request body.

### Get Spotify Access Token

You must implement the Spotify OAuth 2.0 flow. See: [Spotify Authorization Guide](https://developer.spotify.com/documentation/web-api/tutorials/code-flow)

**Required Scopes**:
- `playlist-modify-public`
- `playlist-modify-private`
- `user-read-private`
- `user-read-email`

## Endpoints

### POST /playlist

Creates a new Spotify playlist based on a natural language prompt.

#### Request

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "user_id": "string (required)",
  "prompt": "string (required)",
  "spotify_access_token": "string (required)"
}
```

**Parameters**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | string | Yes | Unique user identifier |
| `prompt` | string | Yes | Natural language description of the desired playlist |
| `spotify_access_token` | string | Yes | Spotify OAuth 2.0 access token |

**Example**:
```json
{
  "user_id": "user123",
  "prompt": "Energetic music for working out, some rock and electronic",
  "spotify_access_token": "BQDxO8F...full_token"
}
```

#### Response

**Success (200 OK)**:
```json
{
  "message": "Playlist created successfully",
  "playlist_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
  "tracks_count": 20,
  "parameters": {
    "genres": ["rock", "electronic"],
    "mood": "energetic",
    "energy": 0.85,
    "danceability": 0.75,
    "valence": 0.7,
    "tempo": 140,
    "popularity": 60,
    "playlist_name": "AI DJ - Workout Energy",
    "limit": 20
  }
}
```

**Error (400 Bad Request)**:
```json
{
  "error": "Missing required parameters: user_id and prompt are required"
}
```

**Error (404 Not Found)**:
```json
{
  "error": "No tracks found matching the criteria"
}
```

**Error (500 Internal Server Error)**:
```json
{
  "error": "Internal server error: {error_message}"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | Success message |
| `playlist_url` | string | Public URL of the playlist on Spotify |
| `tracks_count` | integer | Number of songs added to the playlist |
| `parameters` | object | Musical parameters extracted from the prompt |
| `parameters.genres` | array[string] | Identified musical genres |
| `parameters.mood` | string | Mood of the playlist |
| `parameters.energy` | float | Energy level (0.0 - 1.0) |
| `parameters.danceability` | float | How danceable (0.0 - 1.0) |
| `parameters.valence` | float | Positivity (0.0 - 1.0) |
| `parameters.tempo` | integer | Tempo in BPM (optional) |
| `parameters.popularity` | integer | Minimum popularity (0 - 100) |
| `parameters.playlist_name` | string | Generated name for the playlist |
| `parameters.limit` | integer | Number of requested songs |

## Examples

### cURL

```bash
curl -X POST https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "prompt": "Relaxing music for studying, jazz and lo-fi",
    "spotify_access_token": "BQDxO8F...token"
  }'
```

### PowerShell

```powershell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    user_id = "user123"
    prompt = "Relaxing music for studying, jazz and lo-fi"
    spotify_access_token = "BQDxO8F...token"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist" `
    -Method Post `
    -Headers $headers `
    -Body $body
```

### Python

```python
import requests

url = "https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist"

payload = {
    "user_id": "user123",
    "prompt": "Relaxing music for studying, jazz and lo-fi",
    "spotify_access_token": "BQDxO8F...token"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const url = 'https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist';

const payload = {
  user_id: 'user123',
  prompt: 'Relaxing music for studying, jazz and lo-fi',
  spotify_access_token: 'BQDxO8F...token'
};

axios.post(url, payload)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.error(error.response.data);
  });
```

### JavaScript (Fetch API)

```javascript
const url = 'https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist';

const payload = {
  user_id: 'user123',
  prompt: 'Relaxing music for studying, jazz and lo-fi',
  spotify_access_token: 'BQDxO8F...token'
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

## Prompt Examples

Here are examples of prompts that work well:

### By Activity

```json
{
  "prompt": "Music for running, fast and energetic rhythm"
}
```

```json
{
  "prompt": "Playlist for focused work, instrumental music without lyrics"
}
```

```json
{
  "prompt": "Music for a party, reggaeton and danceable Latin music"
}
```

### By Genre

```json
{
  "prompt": "Classic rock from the 70s and 80s, iconic bands"
}
```

```json
{
  "prompt": "Smooth jazz for a romantic dinner"
}
```

```json
{
  "prompt": "Electronic music for dancing, house and techno"
}
```

### By Mood

```json
{
  "prompt": "Sad music to cry to, emotional ballads"
}
```

```json
{
  "prompt": "Happy and optimistic songs to start the day"
}
```

```json
{
  "prompt": "Relaxing music for meditation and yoga"
}
```

### Complex Combinations

```json
{
  "prompt": "Alternative indie rock from the 2000s, little-known bands, medium tempo"
}
```

```json
{
  "prompt": "Modern Latin music, mix of reggaeton, salsa and bachata, for dancing"
}
```

```json
{
  "prompt": "90s hip hop classics, east coast rap, old school beats"
}
```

## Rate Limits

### API Gateway Defaults

- **Burst**: 5,000 requests
- **Steady-state**: 10,000 requests/second

### Bedrock Limits

- **Requests**: 200 requests/minute
- **Tokens**: 200K input tokens/minute

### Spotify API Limits

- **Rate limit**: Variable by endpoint
- **Retry-After**: Header included in 429 responses

## Error Handling

### Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success - Playlist created successfully |
| 400 | Bad Request - Missing or invalid parameters |
| 401 | Unauthorized - Invalid or expired Spotify token |
| 404 | Not Found - No tracks found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |
| 503 | Service Unavailable - Service temporarily unavailable |

### Error Response Format

```json
{
  "error": "Error description"
}
```

### Common Errors

#### Invalid Spotify Token

```json
{
  "error": "Internal server error: The access token expired"
}
```

**Solution**: Renew the access token using the OAuth 2.0 refresh token.

#### Missing Parameters

```json
{
  "error": "Missing required parameters: user_id and prompt are required"
}
```

**Solution**: Make sure to include `user_id`, `prompt`, and `spotify_access_token`.

#### No Tracks Found

```json
{
  "error": "No tracks found matching the criteria"
}
```

**Solution**: Try with a different or more general prompt.

## CORS

The API has CORS enabled with the following configuration:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

This allows calls from any domain (web frontend).

## Best Practices

### 1. Token Management

- Store the access token securely
- Implement automatic refresh when it expires
- Do not expose the token in URLs or logs

### 2. Error Handling

```javascript
try {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error);
  }
  
  const data = await response.json();
  return data;
} catch (error) {
  console.error('Error creating playlist:', error.message);
  // Handle error appropriately
}
```

### 3. Retry Logic

```python
import time
import requests

def create_playlist_with_retry(payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit - wait and retry
                retry_after = int(e.response.headers.get('Retry-After', 5))
                time.sleep(retry_after)
            elif attempt == max_retries - 1:
                raise
            else:
                time.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Prompt Optimization

**Good prompts**:
- ✅ Specific: "90s alternative rock"
- ✅ Descriptive: "Energetic music for running"
- ✅ With context: "Smooth jazz for a romantic dinner"

**Prompts to avoid**:
- ❌ Too vague: "music"
- ❌ Contradictory: "relaxing and energetic music"
- ❌ Too specific: "only songs exactly 3:45 minutes long"

## Monitoring

### CloudWatch Metrics

You can monitor API usage in CloudWatch:

```powershell
# View API Gateway metrics
aws cloudwatch get-metric-statistics `
  --namespace AWS/ApiGateway `
  --metric-name Count `
  --dimensions Name=ApiId,Value=abc123xyz `
  --start-time 2025-10-10T00:00:00Z `
  --end-time 2025-10-10T23:59:59Z `
  --period 3600 `
  --statistics Sum
```

### CloudWatch Logs

```powershell
# View Lambda logs
aws logs tail /aws/lambda/AI-DJ-Handler --follow
```

## Changelog

### Version 1.0.0 (2025-10-10)

- ✨ Initial release
- 🎵 POST /playlist endpoint
- 🤖 Integration with Amazon Bedrock (Claude 3 Sonnet)
- 🎧 Spotify playlist creation
- 💾 DynamoDB storage for user history

## Support

To report issues or request features:
- GitHub Issues: [your-repo]/issues
- Email: support@ai-dj.com (example)

## License

MIT License - See LICENSE file for details.

---

**API Version**: 1.0.0  
**Last Updated**: 2025-10-10  
**Region**: us-east-1
