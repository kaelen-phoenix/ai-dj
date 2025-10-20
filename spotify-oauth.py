#!/usr/bin/env python3
"""
Script simple para obtener un Spotify Access Token usando OAuth 2.0
Este token SI permite crear playlists.
"""

import http.server
import socketserver
import urllib.parse
import webbrowser
import requests
import base64
from urllib.parse import urlencode

# Tus credenciales de Spotify
CLIENT_ID = "b568dcea222848aab3697ec6ca4195b7"
CLIENT_SECRET = "c1abfc0990574c68a4f8e9d4846190c1"
REDIRECT_URI = "http://localhost:8888/callback"

# Scopes necesarios
SCOPES = "playlist-modify-public playlist-modify-private user-read-private user-read-email"

# Variable global para almacenar el código de autorización
auth_code = None


class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    """Handler para capturar el código de autorización"""
    
    def do_GET(self):
        global auth_code
        
        # Parsear la URL
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/callback':
            # Extraer el código de autorización
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            if 'code' in query_params:
                auth_code = query_params['code'][0]
                
                # Responder al navegador
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <html>
                <head><title>Autorizacion Exitosa</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: green;">Autorizacion Exitosa!</h1>
                    <p>Ya puedes cerrar esta ventana y volver a la terminal.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
            else:
                # Error en la autorización
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                error = query_params.get('error', ['Unknown error'])[0]
                html = f"""
                <html>
                <head><title>Error de Autorizacion</title></head>
                <body style="font-family: Arial; text-align: center; padding: 50px;">
                    <h1 style="color: red;">Error de Autorizacion</h1>
                    <p>Error: {error}</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suprimir logs del servidor
        pass


def get_authorization_code():
    """Abre el navegador para que el usuario autorice la app"""
    
    # Construir URL de autorización
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPES,
        'show_dialog': 'true'  # Siempre mostrar el diálogo de autorización
    }
    
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(auth_params)}"
    
    print("\n[INFO] Abriendo navegador para autorizacion...")
    print(f"Si no se abre automáticamente, ve a: {auth_url}\n")
    
    # Abrir navegador
    webbrowser.open(auth_url)
    
    # Iniciar servidor local para recibir el callback
    PORT = 8888
    with socketserver.TCPServer(("", PORT), OAuthHandler) as httpd:
        print(f"[OK] Servidor local iniciado en http://localhost:{PORT}")
        print("[WAIT] Esperando autorizacion...\n")
        
        # Esperar hasta recibir el código
        while auth_code is None:
            httpd.handle_request()
    
    return auth_code


def exchange_code_for_token(code):
    """Intercambia el código de autorización por un access token"""
    
    # Codificar credenciales en Base64
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    credentials_b64 = base64.b64encode(credentials.encode()).decode()
    
    # Headers
    headers = {
        'Authorization': f'Basic {credentials_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # Body
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    # Solicitar token
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        headers=headers,
        data=data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error obteniendo token: {response.text}")


def main():
    print("=" * 60)
    print("Spotify OAuth 2.0 - Obtener Access Token")
    print("=" * 60)
    
    try:
        # Paso 1: Obtener código de autorización
        code = get_authorization_code()
        
        if not code:
            print("[ERROR] No se pudo obtener el codigo de autorizacion")
            return
        
        print(f"[OK] Codigo de autorizacion obtenido: {code[:20]}...")
        
        # Paso 2: Intercambiar código por token
        print("\n[INFO] Intercambiando codigo por access token...")
        token_data = exchange_code_for_token(code)
        
        # Mostrar resultados
        print("\n" + "=" * 60)
        print("[SUCCESS] ACCESS TOKEN OBTENIDO EXITOSAMENTE!")
        print("=" * 60)
        print(f"\nAccess Token:")
        print(f"{token_data['access_token']}\n")
        print(f"Expira en: {token_data['expires_in']} segundos ({token_data['expires_in'] / 3600:.1f} horas)")
        print(f"Refresh Token: {token_data.get('refresh_token', 'N/A')[:20]}...")
        print(f"Scopes: {token_data.get('scope', 'N/A')}")
        print("\n" + "=" * 60)
        print("Copia el Access Token de arriba y usalo en tu API")
        print("=" * 60)
        
        # Guardar en archivo
        with open('spotify_token.txt', 'w') as f:
            f.write(token_data['access_token'])
        
        print("\n[SAVED] Token guardado en: spotify_token.txt")
        
    except Exception as e:
        print(f"\n[ERROR] Error: {str(e)}")


if __name__ == "__main__":
    main()
