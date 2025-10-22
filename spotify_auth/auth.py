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
    
    print(f"📥 OAuth Callback - Event: {json.dumps(event)}")
    
    # Log request details
    print(f"🔍 Request context: {json.dumps(event.get('requestContext', {}))}")
    print(f"🔍 Query params: {json.dumps(event.get('queryStringParameters', {}))}")
    print(f"🔍 Headers: {json.dumps(event.get('headers', {}))}")
    
    # CORS headers
    headers = {
        'Content-Type': 'text/html',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    
    # Manejar OPTIONS para CORS
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        print("✅ Handling OPTIONS request")
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
    
    print(f"🔑 Env vars - CLIENT_ID: {client_id[:10] if client_id else 'MISSING'}...")
    print(f"🔑 CLIENT_SECRET: {'SET' if client_secret else 'MISSING'}")
    print(f"🔑 REDIRECT_URI: {redirect_uri}")
    
    if not all([client_id, client_secret, redirect_uri]):
        missing = []
        if not client_id: missing.append('CLIENT_ID')
        if not client_secret: missing.append('CLIENT_SECRET')
        if not redirect_uri: missing.append('REDIRECT_URI')
        error_msg = f'Server configuration error - Missing: {", ".join(missing)}'
        print(f"❌ {error_msg}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': create_error_page(error_msg)
        }
    
    # Intercambiar código por token
    try:
        print(f"🔄 Exchanging code for token - code length: {len(code)}")
        token_data = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
        
        print(f"✅ Token exchange successful!")
        print(f"🔑 Access token length: {len(token_data.get('access_token', ''))}")
        print(f"⏱️ Expires in: {token_data.get('expires_in', 'N/A')} seconds")
        
        # Crear página HTML que guarda el token y redirige
        html = create_success_page(token_data)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': html
        }
        
    except Exception as e:
        print(f"❌ Error in token exchange: {str(e)}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #FF9900 0%, #232F3E 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0;
                color: white;
                padding: 20px;
            }}
            .container {{
                background: rgba(0, 0, 0, 0.8);
                padding: 40px;
                border-radius: 20px;
                text-align: center;
                max-width: 500px;
                width: 100%;
            }}
            .spinner {{
                border: 3px solid rgba(255, 153, 0, 0.3);
                border-top: 3px solid #FF9900;
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
                color: #FF9900;
                font-size: 24px;
            }}
            p {{
                font-size: 16px;
            }}
        </style>
        <script>
            // Redirect immediately with token in hash - compatible with mobile
            (function() {{
                console.log('🔄 OAuth Success Page Loaded');
                console.log('🔑 Redirect URL:', '{redirect_url}');
                console.log('🔑 Token length: {len(access_token)}');
                
                // Add visible countdown
                let countdown = 2;
                const countdownEl = document.getElementById('countdown');
                const interval = setInterval(() => {{
                    countdown--;
                    if (countdownEl) countdownEl.textContent = countdown;
                    if (countdown <= 0) {{
                        clearInterval(interval);
                        console.log('🚀 Redirecting now...');
                        try {{
                            window.location.replace('{redirect_url}');
                        }} catch(e) {{
                            console.error('❌ Replace failed, trying href:', e);
                            window.location.href = '{redirect_url}';
                        }}
                    }}
                }}, 1000);
            }})();
        </script>
    </head>
    <body>
        <div class="container">
            <h1>✅ Authentication Successful</h1>
            <div class="spinner"></div>
            <p>Redirecting to AI DJ in <span id="countdown" style="color: #FF9900; font-weight: bold;">2</span> seconds...</p>
            <p style="font-size: 14px; margin-top: 20px; color: #ccc;">
                <strong>Note:</strong> If you used email/password and you're not redirected,<br>
                please click the link below:
            </p>
            <p style="font-size: 12px; margin-top: 10px;">
                <a href="{redirect_url}" style="color: #FF9900; font-size: 16px; text-decoration: underline;">Click here to continue</a>
            </p>
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
