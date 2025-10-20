"""
Lambda function para manejar el callback de Spotify OAuth
Intercambia el código de autorización por un access token
"""

import json
import base64
import os
import urllib.request
import urllib.parse
import urllib.error


def lambda_handler(event, context):
    """Handler para el callback de Spotify OAuth"""
    
    # CORS headers
    headers = {
        'Content-Type': 'text/html',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    
    # Manejar OPTIONS para CORS
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Obtener parámetros de la query string
    query_params = event.get('queryStringParameters', {})
    
    if not query_params:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': create_error_page('No query parameters provided')
        }
    
    # Verificar si hay error
    if 'error' in query_params:
        error = query_params['error']
        return {
            'statusCode': 400,
            'headers': headers,
            'body': create_error_page(f'Spotify authorization error: {error}')
        }
    
    # Obtener el código de autorización
    code = query_params.get('code')
    if not code:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': create_error_page('No authorization code provided')
        }
    
    # Credenciales de Spotify
    client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    redirect_uri = os.environ.get('REDIRECT_URI')
    
    if not all([client_id, client_secret, redirect_uri]):
        return {
            'statusCode': 500,
            'headers': headers,
            'body': create_error_page('Server configuration error')
        }
    
    # Intercambiar código por token
    try:
        token_data = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
        
        # Crear página HTML que guarda el token y redirige
        html = create_success_page(token_data)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': html
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': create_error_page(f'Error exchanging code for token: {str(e)}')
        }


def exchange_code_for_token(code, client_id, client_secret, redirect_uri):
    """Intercambia el código de autorización por un access token"""
    
    # Codificar credenciales en Base64
    credentials = f"{client_id}:{client_secret}"
    credentials_b64 = base64.b64encode(credentials.encode()).decode()
    
    # Preparar la petición
    url = 'https://accounts.spotify.com/api/token'
    
    data = urllib.parse.urlencode({
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    }).encode()
    
    headers = {
        'Authorization': f'Basic {credentials_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req) as response:
            response_data = response.read()
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise Exception(f'Spotify API error: {error_body}')


def create_success_page(token_data):
    """Crea una página HTML de éxito que redirige con el token en el hash"""
    
    access_token = token_data.get('access_token', '')
    expires_in = token_data.get('expires_in', 3600)
    refresh_token = token_data.get('refresh_token', '')
    frontend_url = os.environ.get('FRONTEND_URL', '/')
    
    # Construir URL con token en el hash (fragment)
    redirect_url = f"{frontend_url}#access_token={access_token}&expires_in={expires_in}"
    if refresh_token:
        redirect_url += f"&refresh_token={refresh_token}"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentication Successful</title>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="0;url={redirect_url}">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1DB954 0%, #191414 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
                color: white;
            }}
            .container {{
                background: rgba(0, 0, 0, 0.8);
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                max-width: 500px;
            }}
            .spinner {{
                border: 3px solid rgba(29, 185, 84, 0.3);
                border-top: 3px solid #1DB954;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            h1 {{
                color: #1DB954;
            }}
        </style>
        <script>
            // Redirect immediately with token in hash
            window.location.href = '{redirect_url}';
        </script>
    </head>
    <body>
        <div class="container">
            <h1>✅ Authentication Successful</h1>
            <div class="spinner"></div>
            <p>Redirecting...</p>
        </div>
    </body>
    </html>
    """


def create_error_page(error_message):
    """Crea una página HTML de error"""
    
    frontend_url = os.environ.get('FRONTEND_URL', '/')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authentication Error</title>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1DB954 0%, #191414 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
                color: white;
            }}
            .container {{
                background: rgba(0, 0, 0, 0.8);
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                max-width: 500px;
            }}
            h1 {{
                color: #ff4444;
            }}
            button {{
                background: #1DB954;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 25px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 20px;
            }}
            button:hover {{
                background: #1ed760;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>❌ Authentication Error</h1>
            <p>{error_message}</p>
            <button onclick="window.location.href='{frontend_url}'">Back to Home</button>
        </div>
    </body>
    </html>
    """
