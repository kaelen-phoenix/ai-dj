# 🎧 Spotify Authentication Guide

This guide explains how to implement OAuth 2.0 authentication with Spotify to obtain the `access_token` needed to use the AI DJ API.

## Authentication Flow

AI DJ requires users to authenticate with Spotify to create playlists on their behalf. We use the **Authorization Code Flow** of OAuth 2.0.

```
┌─────────┐                                           ┌──────────┐
│  User   │                                           │ Spotify  │
└────┬────┘                                           └────┬─────┘
     │                                                      │
     │  1. Click on "Login with Spotify"                   │
     ├─────────────────────────────────────────────────────>
     │                                                      │
     │  2. Redirects to Spotify for authorization          │
     │<─────────────────────────────────────────────────────┤
     │                                                      │
     │  3. User approves permissions                       │
     ├─────────────────────────────────────────────────────>
     │                                                      │
     │  4. Redirects with authorization code               │
     │<─────────────────────────────────────────────────────┤
     │                                                      │
┌────┴────┐                                           ┌────┴─────┐
│ Backend │                                           │ Spotify  │
└────┬────┘                                           └────┬─────┘
     │                                                      │
     │  5. Exchange code for access_token                  │
     ├─────────────────────────────────────────────────────>
     │                                                      │
     │  6. Returns access_token + refresh_token            │
     │<─────────────────────────────────────────────────────┤
     │                                                      │
```

## Step 1: Configure the Application in Spotify

### 1.1 Create App in Spotify Developer Dashboard

1. Go to: https://developer.spotify.com/dashboard
2. Log in with your Spotify account
3. Click "Create app"
4. Complete the form:
   - **App name**: AI DJ
   - **App description**: AI-powered playlist generator
   - **Redirect URIs**: 
     - `http://localhost:3000/callback` (development)
     - `https://your-domain.com/callback` (production)
   - **APIs**: Web API
5. Save the **Client ID** and **Client Secret**

### 1.2 Configure Redirect URIs

The Redirect URIs are the URLs to which Spotify will redirect after authorization.

**For local development**:
```
http://localhost:3000/callback
http://localhost:8888/callback
```

**For production**:
```
https://your-domain.com/callback
https://your-domain.com/api/auth/callback
```

## Step 2: Implement the Authorization Flow

### 2.1 Generate Authorization URL

**Python**:
```python
import urllib.parse

def get_spotify_auth_url():
    client_id = "your_client_id"
    redirect_uri = "http://localhost:8888/callback"
    scope = "playlist-modify-public playlist-modify-private user-read-private user-read-email"
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope,
        'show_dialog': 'true'  # Optional: always show authorization dialog
    }
    
    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    return auth_url

# Redirect the user to this URL
print(get_spotify_auth_url())
```

**JavaScript (Node.js)**:
```javascript
const querystring = require('querystring');

function getSpotifyAuthUrl() {
  const clientId = 'your_client_id';
  const redirectUri = 'http://localhost:3000/callback';
  const scope = 'playlist-modify-public playlist-modify-private user-read-private user-read-email';
  
  const params = querystring.stringify({
    client_id: clientId,
    response_type: 'code',
    redirect_uri: redirectUri,
    scope: scope,
    show_dialog: true
  });
  
  return `https://accounts.spotify.com/authorize?${params}`;
}

console.log(getSpotifyAuthUrl());
```

### 2.2 Required Scopes

| Scope | Description |
|-------|-------------|
| `playlist-modify-public` | Create and modify public playlists |
| `playlist-modify-private` | Create and modify private playlists |
| `user-read-private` | Read user's profile information |
| `user-read-email` | Read user's email |

**Optional scopes**:
- `user-library-read`: Read user's library
- `user-top-read`: Read user's top tracks and artists
- `user-read-recently-played`: Read user's playback history

### 2.3 Handle the Callback

After the user authorizes, Spotify will redirect to your `redirect_uri` with a code:

```
http://localhost:8888/callback?code=AQD...code_here
```

**Python (Flask)**:
```python
from flask import Flask, request, redirect
import requests
import base64

app = Flask(__name__)

CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://localhost:8888/callback"

@app.route('/callback')
def callback():
    # Get the authorization code
    code = request.args.get('code')
    
    if not code:
        return "Error: No authorization code received", 400
    
    # Exchange code for access token
    token_url = "https://accounts.spotify.com/api/token"
    
    # Encode credentials in Base64
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_str.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens['access_token']
        refresh_token = tokens['refresh_token']
        expires_in = tokens['expires_in']  # Seconds until expiration
        
        # Save tokens securely (database, session, etc.)
        # ...
        
        return f"Success! Access token: {access_token[:20]}..."
    else:
        return f"Error: {response.json()}", response.status_code

if __name__ == '__main__':
    app.run(port=8888)
```

**JavaScript (Express)**:
```javascript
const express = require('express');
const axios = require('axios');
const querystring = require('querystring');

const app = express();

const CLIENT_ID = 'your_client_id';
const CLIENT_SECRET = 'your_client_secret';
const REDIRECT_URI = 'http://localhost:3000/callback';

app.get('/callback', async (req, res) => {
  const code = req.query.code;
  
  if (!code) {
    return res.status(400).send('Error: No authorization code received');
  }
  
  try {
    // Exchange code for access token
    const tokenUrl = 'https://accounts.spotify.com/api/token';
    
    const authBuffer = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64');
    
    const response = await axios.post(tokenUrl, querystring.stringify({
      grant_type: 'authorization_code',
      code: code,
      redirect_uri: REDIRECT_URI
    }), {
      headers: {
        'Authorization': `Basic ${authBuffer}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    const { access_token, refresh_token, expires_in } = response.data;
    
    // Save tokens securely
    // ...
    
    res.send(`Success! Access token: ${access_token.substring(0, 20)}...`);
  } catch (error) {
    res.status(500).send(`Error: ${error.message}`);
  }
});

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
```

## Step 3: Renew the Access Token

Spotify access tokens expire after 1 hour. Use the `refresh_token` to get a new one.

**Python**:
```python
import requests
import base64

def refresh_access_token(refresh_token):
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    
    token_url = "https://accounts.spotify.com/api/token"
    
    # Encode credentials
    auth_str = f"{client_id}:{client_secret}"
    auth_bytes = auth_str.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        new_access_token = tokens['access_token']
        expires_in = tokens['expires_in']
        
        return new_access_token, expires_in
    else:
        raise Exception(f"Error refreshing token: {response.json()}")

# Usage
new_token, expires_in = refresh_access_token("your_refresh_token")
print(f"New access token: {new_token}")
print(f"Expires in: {expires_in} seconds")
```

**JavaScript**:
```javascript
const axios = require('axios');
const querystring = require('querystring');

async function refreshAccessToken(refreshToken) {
  const clientId = 'your_client_id';
  const clientSecret = 'your_client_secret';
  
  const tokenUrl = 'https://accounts.spotify.com/api/token';
  
  const authBuffer = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');
  
  try {
    const response = await axios.post(tokenUrl, querystring.stringify({
      grant_type: 'refresh_token',
      refresh_token: refreshToken
    }), {
      headers: {
        'Authorization': `Basic ${authBuffer}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    const { access_token, expires_in } = response.data;
    
    return { accessToken: access_token, expiresIn: expires_in };
  } catch (error) {
    throw new Error(`Error refreshing token: ${error.message}`);
  }
}

// Usage
refreshAccessToken('your_refresh_token')
  .then(({ accessToken, expiresIn }) => {
    console.log(`New access token: ${accessToken}`);
    console.log(`Expires in: ${expiresIn} seconds`);
  });
```

## Step 4: Use the Access Token with AI DJ

Once you have the `access_token`, use it to call the AI DJ API:

**Python**:
```python
import requests

def create_playlist(user_id, prompt, access_token):
    api_url = "https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist"
    
    payload = {
        "user_id": user_id,
        "prompt": prompt,
        "spotify_access_token": access_token
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.json()}")

# Usage
result = create_playlist(
    user_id="user123",
    prompt="Energetic music for working out",
    access_token="BQD...your_access_token"
)

print(f"Playlist created: {result['playlist_url']}")
```

## Complete Example: Simple Web Application

### Backend (Flask)

```python
from flask import Flask, request, redirect, session, jsonify
import requests
import base64
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://localhost:8888/callback"
AI_DJ_API = "https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist"

@app.route('/')
def index():
    return '''
        <h1>AI DJ - Spotify Playlist Generator</h1>
        <a href="/login">Login with Spotify</a>
    '''

@app.route('/login')
def login():
    scope = "playlist-modify-public playlist-modify-private user-read-private"
    auth_url = f"https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={scope}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    
    # Exchange code for token
    token_url = "https://accounts.spotify.com/api/token"
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_base64 = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(token_url, headers=headers, data=data)
    tokens = response.json()
    
    # Save to session
    session['access_token'] = tokens['access_token']
    session['refresh_token'] = tokens['refresh_token']
    
    return redirect('/create')

@app.route('/create')
def create():
    if 'access_token' not in session:
        return redirect('/login')
    
    return '''
        <h1>Create Playlist</h1>
        <form action="/generate" method="post">
            <input type="text" name="prompt" placeholder="Describe your playlist" required>
            <button type="submit">Generate</button>
        </form>
    '''

@app.route('/generate', methods=['POST'])
def generate():
    if 'access_token' not in session:
        return redirect('/login')
    
    prompt = request.form.get('prompt')
    
    # Call AI DJ API
    payload = {
        "user_id": "user123",  # In production, use real user ID
        "prompt": prompt,
        "spotify_access_token": session['access_token']
    }
    
    response = requests.post(AI_DJ_API, json=payload)
    result = response.json()
    
    if response.status_code == 200:
        playlist_url = result['playlist_url']
        return f'''
            <h1>Playlist Created!</h1>
            <p>Prompt: {prompt}</p>
            <p><a href="{playlist_url}" target="_blank">Open in Spotify</a></p>
            <p><a href="/create">Create Another</a></p>
        '''
    else:
        return f"Error: {result.get('error', 'Unknown error')}"

if __name__ == '__main__':
    app.run(port=8888, debug=True)
```

### Frontend (HTML + JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
    <title>AI DJ</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
        }
        input, button {
            padding: 10px;
            margin: 10px 0;
            width: 100%;
        }
        button {
            background-color: #1DB954;
            color: white;
            border: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>🎵 AI DJ</h1>
    <div id="login-section">
        <button onclick="loginWithSpotify()">Login with Spotify</button>
    </div>
    <div id="create-section" style="display: none;">
        <input type="text" id="prompt" placeholder="Describe your playlist...">
        <button onclick="createPlaylist()">Generate Playlist</button>
        <div id="result"></div>
    </div>

    <script>
        // Check for token in URL (after callback)
        const urlParams = new URLSearchParams(window.location.search);
        const accessToken = urlParams.get('access_token');
        
        if (accessToken) {
            localStorage.setItem('spotify_token', accessToken);
            document.getElementById('login-section').style.display = 'none';
            document.getElementById('create-section').style.display = 'block';
        } else if (localStorage.getItem('spotify_token')) {
            document.getElementById('login-section').style.display = 'none';
            document.getElementById('create-section').style.display = 'block';
        }

        function loginWithSpotify() {
            const clientId = 'your_client_id';
            const redirectUri = 'http://localhost:8888/callback';
            const scope = 'playlist-modify-public playlist-modify-private user-read-private';
            
            const authUrl = `https://accounts.spotify.com/authorize?client_id=${clientId}&response_type=token&redirect_uri=${redirectUri}&scope=${scope}`;
            
            window.location.href = authUrl;
        }

        async function createPlaylist() {
            const prompt = document.getElementById('prompt').value;
            const token = localStorage.getItem('spotify_token');
            
            if (!prompt) {
                alert('Please enter a prompt');
                return;
            }

            const apiUrl = 'https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist';
            
            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: 'user123',
                        prompt: prompt,
                        spotify_access_token: token
                    })
                });

                const result = await response.json();

                if (response.ok) {
                    document.getElementById('result').innerHTML = `
                        <h2>Playlist Created! 🎉</h2>
                        <p><a href="${result.playlist_url}" target="_blank">Open in Spotify</a></p>
                        <p>Tracks: ${result.tracks_count}</p>
                    `;
                } else {
                    document.getElementById('result').innerHTML = `
                        <p style="color: red;">Error: ${result.error}</p>
                    `;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = `
                    <p style="color: red;">Error: ${error.message}</p>
                `;
            }
        }
    </script>
</body>
</html>
```

## Security and Best Practices

### 1. Token Storage

**❌ DO NOT**:
- Save tokens in localStorage (vulnerable to XSS)
- Expose tokens in URLs
- Hardcode Client Secret in the frontend

**✅ DO**:
- Save tokens in HttpOnly cookies
- Use server-side sessions
- Encrypt tokens in the database
- Implement PKCE for public applications

### 2. Automatic Renewal

```python
import time
from datetime import datetime, timedelta

class SpotifyTokenManager:
    def __init__(self, access_token, refresh_token, expires_in):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = datetime.now() + timedelta(seconds=expires_in)
    
    def get_valid_token(self):
        # If the token expires in less than 5 minutes, renew it
        if datetime.now() >= self.expires_at - timedelta(minutes=5):
            self.refresh()
        return self.access_token
    
    def refresh(self):
        new_token, expires_in = refresh_access_token(self.refresh_token)
        self.access_token = new_token
        self.expires_at = datetime.now() + timedelta(seconds=expires_in)

# Usage
token_manager = SpotifyTokenManager(access_token, refresh_token, 3600)
current_token = token_manager.get_valid_token()
```

### 3. Error Handling

```python
def call_ai_dj_with_retry(user_id, prompt, token_manager, max_retries=2):
    for attempt in range(max_retries):
        try:
            token = token_manager.get_valid_token()
            result = create_playlist(user_id, prompt, token)
            return result
        except Exception as e:
            if "token" in str(e).lower() and attempt < max_retries - 1:
                # Invalid token, force refresh
                token_manager.refresh()
            else:
                raise
```

## Additional Resources

- **Spotify OAuth 2.0 Guide**: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
- **Spotify API Reference**: https://developer.spotify.com/documentation/web-api/reference/
- **OAuth 2.0 RFC**: https://datatracker.ietf.org/doc/html/rfc6749
- **PKCE Extension**: https://datatracker.ietf.org/doc/html/rfc7636

## Troubleshooting

### Error: "Invalid redirect URI"

**Cause**: The redirect URI does not match the one configured in the Spotify Dashboard.

**Solution**: Verify that the URI is exactly the same (including protocol, port, and path).

### Error: "Invalid client"

**Cause**: Incorrect Client ID or Client Secret.

**Solution**: Verify the credentials in the Spotify Developer Dashboard.

### Error: "The access token expired"

**Cause**: The access token has expired (after 1 hour).

**Solution**: Use the refresh token to get a new one.

---

**Need help?** Check the [official Spotify documentation](https://developer.spotify.com/documentation/).
