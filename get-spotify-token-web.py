#!/usr/bin/env python3
"""
Servidor web simple para obtener token de Spotify OAuth 2.0
Abre automaticamente el navegador y te guia paso a paso
"""

import webbrowser
import http.server
import socketserver
import urllib.parse
import requests
import base64
from threading import Timer

# Configuracion
CLIENT_ID = "b568dcea222848aab3697ec6ca4195b7"
CLIENT_SECRET = "c1abfc0990574c68a4f8e9d4846190c1"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPES = "playlist-modify-public playlist-modify-private user-read-private user-read-email"

# Variable global para el token
access_token = None

class SpotifyAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global access_token
        
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/':
            # Pagina principal - mostrar boton para autorizar
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            auth_params = {
                'client_id': CLIENT_ID,
                'response_type': 'code',
                'redirect_uri': REDIRECT_URI,
                'scope': SCOPES,
                'show_dialog': 'true'
            }
            auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode(auth_params)}"
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Spotify OAuth - AI DJ</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        background: linear-gradient(135deg, #1DB954 0%, #191414 100%);
                        color: white;
                    }}
                    .container {{
                        background: rgba(0,0,0,0.7);
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                    }}
                    h1 {{
                        color: #1DB954;
                        text-align: center;
                    }}
                    .btn {{
                        display: block;
                        width: 100%;
                        padding: 15px;
                        margin: 20px 0;
                        background: #1DB954;
                        color: white;
                        text-decoration: none;
                        text-align: center;
                        border-radius: 25px;
                        font-size: 18px;
                        font-weight: bold;
                        transition: background 0.3s;
                    }}
                    .btn:hover {{
                        background: #1ed760;
                    }}
                    .steps {{
                        background: rgba(255,255,255,0.1);
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .step {{
                        margin: 10px 0;
                        padding-left: 25px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎵 Obtener Token de Spotify</h1>
                    <p style="text-align: center; font-size: 18px;">AI DJ - Generador de Playlists</p>
                    
                    <div class="steps">
                        <h3>Pasos:</h3>
                        <div class="step">1. Click en el boton verde abajo</div>
                        <div class="step">2. Inicia sesion en Spotify (si es necesario)</div>
                        <div class="step">3. Autoriza la aplicacion AI DJ</div>
                        <div class="step">4. Seras redirigido automaticamente</div>
                        <div class="step">5. Copia el token que aparecera</div>
                    </div>
                    
                    <a href="{auth_url}" class="btn">
                        AUTORIZAR CON SPOTIFY
                    </a>
                    
                    <p style="text-align: center; font-size: 12px; color: #aaa; margin-top: 30px;">
                        Este servidor se cerrara automaticamente despues de obtener el token
                    </p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
            
        elif parsed_path.path == '/callback':
            # Callback de Spotify
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            if 'code' in query_params:
                code = query_params['code'][0]
                
                # Intercambiar codigo por token
                try:
                    token_data = exchange_code_for_token(code)
                    access_token = token_data['access_token']
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Token Obtenido!</title>
                        <style>
                            body {{
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                max-width: 800px;
                                margin: 50px auto;
                                padding: 20px;
                                background: linear-gradient(135deg, #1DB954 0%, #191414 100%);
                                color: white;
                            }}
                            .container {{
                                background: rgba(0,0,0,0.7);
                                padding: 40px;
                                border-radius: 10px;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                            }}
                            h1 {{
                                color: #1DB954;
                                text-align: center;
                            }}
                            .token-box {{
                                background: rgba(255,255,255,0.1);
                                padding: 20px;
                                border-radius: 5px;
                                margin: 20px 0;
                                word-break: break-all;
                                font-family: 'Courier New', monospace;
                                font-size: 14px;
                            }}
                            .btn {{
                                display: inline-block;
                                padding: 10px 20px;
                                background: #1DB954;
                                color: white;
                                text-decoration: none;
                                border-radius: 5px;
                                cursor: pointer;
                                border: none;
                                font-size: 16px;
                            }}
                            .btn:hover {{
                                background: #1ed760;
                            }}
                            .success {{
                                color: #1DB954;
                                font-size: 48px;
                                text-align: center;
                            }}
                        </style>
                        <script>
                            function copyToken() {{
                                const token = document.getElementById('token').innerText;
                                navigator.clipboard.writeText(token).then(() => {{
                                    alert('Token copiado al portapapeles!');
                                }});
                            }}
                        </script>
                    </head>
                    <body>
                        <div class="container">
                            <div class="success">✅</div>
                            <h1>Token Obtenido Exitosamente!</h1>
                            
                            <h3>Tu Access Token:</h3>
                            <div class="token-box" id="token">{access_token}</div>
                            
                            <button class="btn" onclick="copyToken()">📋 COPIAR TOKEN</button>
                            
                            <h3 style="margin-top: 30px;">Informacion:</h3>
                            <ul>
                                <li>Expira en: {token_data.get('expires_in', 3600)} segundos ({token_data.get('expires_in', 3600) / 3600:.1f} horas)</li>
                                <li>Scopes: {token_data.get('scope', 'N/A')}</li>
                                <li>Token guardado en: <code>spotify_token_oauth.txt</code></li>
                            </ul>
                            
                            <p style="text-align: center; margin-top: 30px; color: #1DB954;">
                                Puedes cerrar esta ventana y volver a la terminal
                            </p>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode('utf-8'))
                    
                    # Guardar token en archivo
                    with open('spotify_token_oauth.txt', 'w') as f:
                        f.write(access_token)
                    
                    # Cerrar servidor despues de 5 segundos
                    Timer(5.0, lambda: httpd.shutdown()).start()
                    
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>Error</title></head>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1 style="color: red;">Error al obtener token</h1>
                        <p>{str(e)}</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode('utf-8'))
            else:
                error = query_params.get('error', ['Unknown'])[0]
                self.send_response(400)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Error</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">Error de Autorizacion</h1>
                    <p>Error: {error}</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        pass  # Suprimir logs


def exchange_code_for_token(code):
    """Intercambiar codigo por token"""
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    credentials_b64 = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {credentials_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        headers=headers,
        data=data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.text}")


if __name__ == "__main__":
    PORT = 8888
    
    print("=" * 60)
    print("Spotify OAuth 2.0 - Servidor Web")
    print("=" * 60)
    print(f"\n[INFO] Servidor iniciado en: http://localhost:{PORT}")
    print("[INFO] Abriendo navegador...")
    print("\nSigue las instrucciones en el navegador\n")
    print("=" * 60)
    
    # Abrir navegador
    Timer(1.0, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
    
    # Iniciar servidor
    with socketserver.TCPServer(("", PORT), SpotifyAuthHandler) as httpd:
        httpd.serve_forever()
    
    if access_token:
        print("\n" + "=" * 60)
        print("[SUCCESS] Token obtenido y guardado!")
        print("=" * 60)
        print(f"\nToken: {access_token[:50]}...")
        print(f"Archivo: spotify_token_oauth.txt")
        print("\n" + "=" * 60)
    else:
        print("\n[ERROR] No se pudo obtener el token")
