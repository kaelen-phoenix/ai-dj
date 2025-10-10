# 🎧 Guía de Autenticación con Spotify

Esta guía explica cómo implementar la autenticación OAuth 2.0 con Spotify para obtener el `access_token` necesario para usar la API de AI DJ.

## Flujo de Autenticación

AI DJ requiere que los usuarios se autentiquen con Spotify para poder crear playlists en su nombre. Utilizamos el **Authorization Code Flow** de OAuth 2.0.

```
┌─────────┐                                           ┌──────────┐
│ Usuario │                                           │ Spotify  │
└────┬────┘                                           └────┬─────┘
     │                                                      │
     │  1. Clic en "Login with Spotify"                    │
     ├─────────────────────────────────────────────────────>
     │                                                      │
     │  2. Redirige a Spotify para autorización            │
     │<─────────────────────────────────────────────────────┤
     │                                                      │
     │  3. Usuario aprueba permisos                        │
     ├─────────────────────────────────────────────────────>
     │                                                      │
     │  4. Redirige con código de autorización             │
     │<─────────────────────────────────────────────────────┤
     │                                                      │
┌────┴────┐                                           ┌────┴─────┐
│ Backend │                                           │ Spotify  │
└────┬────┘                                           └────┬─────┘
     │                                                      │
     │  5. Intercambia código por access_token             │
     ├─────────────────────────────────────────────────────>
     │                                                      │
     │  6. Devuelve access_token + refresh_token           │
     │<─────────────────────────────────────────────────────┤
     │                                                      │
```

## Paso 1: Configurar la Aplicación en Spotify

### 1.1 Crear App en Spotify Developer Dashboard

1. Ve a: https://developer.spotify.com/dashboard
2. Inicia sesión con tu cuenta de Spotify
3. Haz clic en "Create app"
4. Completa el formulario:
   - **App name**: AI DJ
   - **App description**: AI-powered playlist generator
   - **Redirect URIs**: 
     - `http://localhost:3000/callback` (desarrollo)
     - `https://tu-dominio.com/callback` (producción)
   - **APIs**: Web API
5. Guarda el **Client ID** y **Client Secret**

### 1.2 Configurar Redirect URIs

Las Redirect URIs son las URLs a las que Spotify redirigirá después de la autorización.

**Para desarrollo local**:
```
http://localhost:3000/callback
http://localhost:8888/callback
```

**Para producción**:
```
https://tu-dominio.com/callback
https://tu-dominio.com/api/auth/callback
```

## Paso 2: Implementar el Flujo de Autorización

### 2.1 Generar URL de Autorización

**Python**:
```python
import urllib.parse

def get_spotify_auth_url():
    client_id = "tu_client_id"
    redirect_uri = "http://localhost:8888/callback"
    scope = "playlist-modify-public playlist-modify-private user-read-private user-read-email"
    
    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope,
        'show_dialog': 'true'  # Opcional: siempre mostrar diálogo de autorización
    }
    
    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(params)}"
    return auth_url

# Redirigir al usuario a esta URL
print(get_spotify_auth_url())
```

**JavaScript (Node.js)**:
```javascript
const querystring = require('querystring');

function getSpotifyAuthUrl() {
  const clientId = 'tu_client_id';
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

### 2.2 Scopes Necesarios

| Scope | Descripción |
|-------|-------------|
| `playlist-modify-public` | Crear y modificar playlists públicas |
| `playlist-modify-private` | Crear y modificar playlists privadas |
| `user-read-private` | Leer información del perfil del usuario |
| `user-read-email` | Leer el email del usuario |

**Scopes opcionales**:
- `user-library-read`: Leer la biblioteca del usuario
- `user-top-read`: Leer las canciones y artistas más escuchados
- `user-read-recently-played`: Leer el historial de reproducción

### 2.3 Manejar el Callback

Después de que el usuario autorice, Spotify redirigirá a tu `redirect_uri` con un código:

```
http://localhost:8888/callback?code=AQD...codigo_aqui
```

**Python (Flask)**:
```python
from flask import Flask, request, redirect
import requests
import base64

app = Flask(__name__)

CLIENT_ID = "tu_client_id"
CLIENT_SECRET = "tu_client_secret"
REDIRECT_URI = "http://localhost:8888/callback"

@app.route('/callback')
def callback():
    # Obtener el código de autorización
    code = request.args.get('code')
    
    if not code:
        return "Error: No authorization code received", 400
    
    # Intercambiar código por access token
    token_url = "https://accounts.spotify.com/api/token"
    
    # Codificar credenciales en Base64
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
        expires_in = tokens['expires_in']  # Segundos hasta expiración
        
        # Guardar tokens de forma segura (base de datos, sesión, etc.)
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

const CLIENT_ID = 'tu_client_id';
const CLIENT_SECRET = 'tu_client_secret';
const REDIRECT_URI = 'http://localhost:3000/callback';

app.get('/callback', async (req, res) => {
  const code = req.query.code;
  
  if (!code) {
    return res.status(400).send('Error: No authorization code received');
  }
  
  try {
    // Intercambiar código por access token
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
    
    // Guardar tokens de forma segura
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

## Paso 3: Renovar el Access Token

Los access tokens de Spotify expiran después de 1 hora. Usa el `refresh_token` para obtener uno nuevo.

**Python**:
```python
import requests
import base64

def refresh_access_token(refresh_token):
    client_id = "tu_client_id"
    client_secret = "tu_client_secret"
    
    token_url = "https://accounts.spotify.com/api/token"
    
    # Codificar credenciales
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

# Uso
new_token, expires_in = refresh_access_token("tu_refresh_token")
print(f"New access token: {new_token}")
print(f"Expires in: {expires_in} seconds")
```

**JavaScript**:
```javascript
const axios = require('axios');
const querystring = require('querystring');

async function refreshAccessToken(refreshToken) {
  const clientId = 'tu_client_id';
  const clientSecret = 'tu_client_secret';
  
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

// Uso
refreshAccessToken('tu_refresh_token')
  .then(({ accessToken, expiresIn }) => {
    console.log(`New access token: ${accessToken}`);
    console.log(`Expires in: ${expiresIn} seconds`);
  });
```

## Paso 4: Usar el Access Token con AI DJ

Una vez que tengas el `access_token`, úsalo para llamar a la API de AI DJ:

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

# Uso
result = create_playlist(
    user_id="usuario123",
    prompt="Música energética para hacer ejercicio",
    access_token="BQD...tu_access_token"
)

print(f"Playlist creada: {result['playlist_url']}")
```

## Ejemplo Completo: Aplicación Web Simple

### Backend (Flask)

```python
from flask import Flask, request, redirect, session, jsonify
import requests
import base64
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

CLIENT_ID = "tu_client_id"
CLIENT_SECRET = "tu_client_secret"
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
    
    # Intercambiar código por token
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
    
    # Guardar en sesión
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
    
    # Llamar a AI DJ API
    payload = {
        "user_id": "user123",  # En producción, usar ID real del usuario
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
        // Verificar si hay token en URL (después de callback)
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
            const clientId = 'tu_client_id';
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

## Seguridad y Mejores Prácticas

### 1. Almacenamiento de Tokens

**❌ NO hacer**:
- Guardar tokens en localStorage (vulnerable a XSS)
- Exponer tokens en URLs
- Hardcodear Client Secret en frontend

**✅ Hacer**:
- Guardar tokens en cookies HttpOnly
- Usar sesiones del lado del servidor
- Encriptar tokens en base de datos
- Implementar PKCE para aplicaciones públicas

### 2. Renovación Automática

```python
import time
from datetime import datetime, timedelta

class SpotifyTokenManager:
    def __init__(self, access_token, refresh_token, expires_in):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = datetime.now() + timedelta(seconds=expires_in)
    
    def get_valid_token(self):
        # Si el token expira en menos de 5 minutos, renovarlo
        if datetime.now() >= self.expires_at - timedelta(minutes=5):
            self.refresh()
        return self.access_token
    
    def refresh(self):
        new_token, expires_in = refresh_access_token(self.refresh_token)
        self.access_token = new_token
        self.expires_at = datetime.now() + timedelta(seconds=expires_in)

# Uso
token_manager = SpotifyTokenManager(access_token, refresh_token, 3600)
current_token = token_manager.get_valid_token()
```

### 3. Manejo de Errores

```python
def call_ai_dj_with_retry(user_id, prompt, token_manager, max_retries=2):
    for attempt in range(max_retries):
        try:
            token = token_manager.get_valid_token()
            result = create_playlist(user_id, prompt, token)
            return result
        except Exception as e:
            if "token" in str(e).lower() and attempt < max_retries - 1:
                # Token inválido, forzar refresh
                token_manager.refresh()
            else:
                raise
```

## Recursos Adicionales

- **Spotify OAuth 2.0 Guide**: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
- **Spotify API Reference**: https://developer.spotify.com/documentation/web-api/reference/
- **OAuth 2.0 RFC**: https://datatracker.ietf.org/doc/html/rfc6749
- **PKCE Extension**: https://datatracker.ietf.org/doc/html/rfc7636

## Troubleshooting

### Error: "Invalid redirect URI"

**Causa**: La redirect URI no coincide con la configurada en Spotify Dashboard.

**Solución**: Verifica que la URI sea exactamente igual (incluyendo protocolo, puerto, y path).

### Error: "Invalid client"

**Causa**: Client ID o Client Secret incorrectos.

**Solución**: Verifica las credenciales en Spotify Developer Dashboard.

### Error: "The access token expired"

**Causa**: El access token ha expirado (después de 1 hora).

**Solución**: Usa el refresh token para obtener uno nuevo.

---

**¿Necesitas ayuda?** Consulta la [documentación oficial de Spotify](https://developer.spotify.com/documentation/).
