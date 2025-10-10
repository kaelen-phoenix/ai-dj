import json
import os
import boto3
import requests
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime


# Configuración de clientes AWS
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Variables de entorno
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

# Tabla DynamoDB
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Manejador principal de la función Lambda.
    Recibe una petición con user_id y prompt, genera una playlist de Spotify.
    """
    try:
        # Parsear el body de la petición
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        prompt = body.get('prompt')
        spotify_access_token = body.get('spotify_access_token')
        
        # Validar parámetros requeridos
        if not user_id or not prompt:
            return create_response(400, {
                'error': 'Missing required parameters: user_id and prompt are required'
            })
        
        if not spotify_access_token:
            return create_response(400, {
                'error': 'Missing spotify_access_token. User must authenticate with Spotify first.'
            })
        
        print(f"Processing request for user_id: {user_id}, prompt: {prompt}")
        
        # Paso 1: Interpretar el prompt con Amazon Bedrock
        music_parameters = interpret_prompt_with_bedrock(prompt)
        print(f"Extracted music parameters: {music_parameters}")
        
        # Paso 2: Buscar canciones en Spotify
        tracks = search_spotify_tracks(music_parameters, spotify_access_token)
        
        if not tracks:
            return create_response(404, {
                'error': 'No tracks found matching the criteria'
            })
        
        print(f"Found {len(tracks)} tracks")
        
        # Paso 3: Crear playlist en Spotify
        playlist_url = create_spotify_playlist(
            user_id=user_id,
            playlist_name=music_parameters.get('playlist_name', f"AI DJ - {prompt[:30]}"),
            track_uris=[track['uri'] for track in tracks],
            access_token=spotify_access_token
        )
        
        print(f"Created playlist: {playlist_url}")
        
        # Paso 4: Guardar en DynamoDB
        save_playlist_to_dynamodb(user_id, playlist_url, prompt, music_parameters)
        
        # Respuesta exitosa
        return create_response(200, {
            'message': 'Playlist created successfully',
            'playlist_url': playlist_url,
            'tracks_count': len(tracks),
            'parameters': music_parameters
        })
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return create_response(500, {
            'error': f'Internal server error: {str(e)}'
        })


def interpret_prompt_with_bedrock(prompt: str) -> Dict[str, Any]:
    """
    Usa Amazon Bedrock para interpretar el prompt del usuario y extraer parámetros musicales.
    """
    system_prompt = """Eres un experto en música que interpreta peticiones de usuarios para crear playlists.
Analiza el prompt del usuario y extrae los siguientes parámetros en formato JSON:

- genres: lista de géneros musicales (ej: ["pop", "rock", "electronic"])
- mood: el estado de ánimo (ej: "happy", "sad", "energetic", "chill", "party")
- energy: nivel de energía de 0.0 a 1.0
- danceability: qué tan bailable de 0.0 a 1.0
- valence: positividad de 0.0 a 1.0 (0 = triste, 1 = feliz)
- tempo: tempo aproximado en BPM (opcional)
- popularity: popularidad mínima de 0 a 100
- playlist_name: nombre sugerido para la playlist
- limit: número de canciones (por defecto 20, máximo 50)

Responde SOLO con el JSON, sin texto adicional."""

    user_message = f"Crea una playlist basada en: {prompt}"
    
    # Preparar el payload para Claude 3
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.7,
        "messages": [
            {
                "role": "user",
                "content": f"{system_prompt}\n\n{user_message}"
            }
        ]
    }
    
    try:
        # Invocar Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(payload)
        )
        
        # Parsear respuesta
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Extraer JSON de la respuesta
        # Claude puede devolver el JSON con o sin markdown
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        music_params = json.loads(content)
        
        # Valores por defecto
        defaults = {
            'genres': ['pop'],
            'mood': 'happy',
            'energy': 0.5,
            'danceability': 0.5,
            'valence': 0.5,
            'popularity': 50,
            'playlist_name': 'AI DJ Playlist',
            'limit': 20
        }
        
        # Combinar con defaults
        return {**defaults, **music_params}
        
    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        # Fallback a parámetros por defecto
        return {
            'genres': ['pop'],
            'mood': 'happy',
            'energy': 0.5,
            'danceability': 0.5,
            'valence': 0.5,
            'popularity': 50,
            'playlist_name': f'AI DJ - {prompt[:30]}',
            'limit': 20
        }


def get_spotify_client_token() -> Optional[str]:
    """
    Obtiene un token de acceso de Spotify usando Client Credentials Flow.
    Este token solo permite búsquedas, no crear playlists.
    """
    auth_url = 'https://accounts.spotify.com/api/token'
    
    # Codificar credenciales en Base64
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_str.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'client_credentials'
    }
    
    try:
        response = requests.post(auth_url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        print(f"Error getting Spotify token: {str(e)}")
        return None


def search_spotify_tracks(parameters: Dict[str, Any], access_token: str) -> List[Dict[str, Any]]:
    """
    Busca canciones en Spotify basándose en los parámetros musicales.
    """
    # Usar el token del usuario para búsquedas
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Construir query de búsqueda
    genres = parameters.get('genres', ['pop'])
    genre_query = ' OR '.join([f'genre:"{g}"' for g in genres[:2]])  # Máximo 2 géneros
    
    search_url = 'https://api.spotify.com/v1/search'
    search_params = {
        'q': genre_query,
        'type': 'track',
        'limit': 50,  # Buscar más para luego filtrar
        'market': 'US'
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=search_params, timeout=10)
        response.raise_for_status()
        tracks_data = response.json()
        
        # Obtener IDs de las canciones
        track_ids = [track['id'] for track in tracks_data['tracks']['items']]
        
        if not track_ids:
            return []
        
        # Obtener audio features para filtrar
        features_url = 'https://api.spotify.com/v1/audio-features'
        features_params = {
            'ids': ','.join(track_ids[:50])  # Máximo 50 IDs
        }
        
        features_response = requests.get(features_url, headers=headers, params=features_params, timeout=10)
        features_response.raise_for_status()
        audio_features = features_response.json()['audio_features']
        
        # Filtrar canciones basándose en parámetros
        filtered_tracks = []
        target_energy = parameters.get('energy', 0.5)
        target_danceability = parameters.get('danceability', 0.5)
        target_valence = parameters.get('valence', 0.5)
        min_popularity = parameters.get('popularity', 50)
        limit = min(parameters.get('limit', 20), 50)
        
        for track, features in zip(tracks_data['tracks']['items'], audio_features):
            if features is None:
                continue
            
            # Calcular score de similitud
            energy_diff = abs(features['energy'] - target_energy)
            dance_diff = abs(features['danceability'] - target_danceability)
            valence_diff = abs(features['valence'] - target_valence)
            
            score = 1 - (energy_diff + dance_diff + valence_diff) / 3
            
            # Filtrar por popularidad
            if track['popularity'] >= min_popularity:
                filtered_tracks.append({
                    'uri': track['uri'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'score': score
                })
        
        # Ordenar por score y tomar los mejores
        filtered_tracks.sort(key=lambda x: x['score'], reverse=True)
        return filtered_tracks[:limit]
        
    except Exception as e:
        print(f"Error searching Spotify tracks: {str(e)}")
        return []


def create_spotify_playlist(
    user_id: str,
    playlist_name: str,
    track_uris: List[str],
    access_token: str
) -> str:
    """
    Crea una nueva playlist en Spotify y añade las canciones.
    Requiere el access token del usuario (con scope playlist-modify-public o playlist-modify-private).
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Obtener el Spotify user ID del token
        profile_url = 'https://api.spotify.com/v1/me'
        profile_response = requests.get(profile_url, headers=headers, timeout=10)
        profile_response.raise_for_status()
        spotify_user_id = profile_response.json()['id']
        
        # Crear playlist
        create_url = f'https://api.spotify.com/v1/users/{spotify_user_id}/playlists'
        create_data = {
            'name': playlist_name,
            'description': f'Created by AI DJ - {datetime.utcnow().strftime("%Y-%m-%d %H:%M")} UTC',
            'public': True
        }
        
        create_response = requests.post(create_url, headers=headers, json=create_data, timeout=10)
        create_response.raise_for_status()
        playlist_id = create_response.json()['id']
        playlist_url = create_response.json()['external_urls']['spotify']
        
        # Añadir canciones a la playlist
        if track_uris:
            add_tracks_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
            add_tracks_data = {
                'uris': track_uris
            }
            
            add_response = requests.post(add_tracks_url, headers=headers, json=add_tracks_data, timeout=10)
            add_response.raise_for_status()
        
        return playlist_url
        
    except Exception as e:
        print(f"Error creating Spotify playlist: {str(e)}")
        raise


def save_playlist_to_dynamodb(
    user_id: str,
    playlist_url: str,
    prompt: str,
    parameters: Dict[str, Any]
) -> None:
    """
    Guarda la información de la playlist en DynamoDB.
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        
        # Obtener playlists existentes del usuario
        response = table.get_item(Key={'user_id': user_id})
        
        if 'Item' in response:
            # Usuario existe, añadir nueva playlist
            playlists = response['Item'].get('playlists', [])
        else:
            # Nuevo usuario
            playlists = []
        
        # Añadir nueva playlist
        playlists.append({
            'playlist_url': playlist_url,
            'prompt': prompt,
            'parameters': parameters,
            'created_at': timestamp
        })
        
        # Guardar en DynamoDB
        table.put_item(
            Item={
                'user_id': user_id,
                'playlists': playlists,
                'last_updated': timestamp
            }
        )
        
        print(f"Saved playlist to DynamoDB for user {user_id}")
        
    except Exception as e:
        print(f"Error saving to DynamoDB: {str(e)}")
        # No lanzar excepción, la playlist ya fue creada


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crea una respuesta HTTP formateada para API Gateway.
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps(body)
    }
