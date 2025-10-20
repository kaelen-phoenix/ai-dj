import json
import os
import boto3
import requests
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime


# AWS Client Configuration
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Environment Variables
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

# DynamoDB Table
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main handler for the Lambda function.
    Receives a request with user_id and prompt, then generates a Spotify playlist.
    """
    try:
        # Parse the request body
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        prompt = body.get('prompt')
        spotify_access_token = body.get('spotify_access_token')
        
        # Validate required parameters
        if not user_id or not prompt:
            return create_response(400, {
                'error': 'Missing required parameters: user_id and prompt are required'
            })
        
        if not spotify_access_token:
            return create_response(400, {
                'error': 'Missing spotify_access_token. User must authenticate with Spotify first.'
            })
        
        print(f"Processing request for user_id: {user_id}, prompt: {prompt}")
        
        # Step 1: Interpret the prompt with Amazon Bedrock
        music_parameters = interpret_prompt_with_bedrock(prompt)
        print(f"Extracted music parameters: {music_parameters}")
        
        # Step 2: Search for tracks on Spotify
        tracks = search_spotify_tracks(music_parameters, spotify_access_token)
        
        if not tracks:
            return create_response(404, {
                'error': 'No tracks found matching the criteria'
            })
        
        print(f"Found {len(tracks)} tracks")
        
        # Step 3: Create a playlist on Spotify
        playlist_url = create_spotify_playlist(
            user_id=user_id,
            playlist_name=music_parameters.get('playlist_name', f"AI DJ - {prompt[:30]}"),
            track_uris=[track['uri'] for track in tracks],
            access_token=spotify_access_token
        )
        
        print(f"Created playlist: {playlist_url}")
        
        # Step 4: Save to DynamoDB
        save_playlist_to_dynamodb(user_id, playlist_url, prompt, music_parameters)
        
        # Successful response
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
    Uses Amazon Bedrock to interpret the user's prompt and extract musical parameters.
    """
    system_prompt = """You are a music expert who interprets user requests to create playlists.
Analyze the user's prompt and extract the following parameters in JSON format:

- genres: list of musical genres (e.g., ["pop", "rock", "electronic"])
- mood: the mood (e.g., "happy", "sad", "energetic", "chill", "party")
- energy: energy level from 0.0 to 1.0
- danceability: how danceable from 0.0 to 1.0
- valence: positivity from 0.0 to 1.0 (0 = sad, 1 = happy)
- tempo: approximate tempo in BPM (optional)
- popularity: minimum popularity from 0 to 100
- playlist_name: suggested name for the playlist
- limit: number of songs (default 20, maximum 50)

Respond ONLY with the JSON, without additional text."""

    user_message = f"Create a playlist based on: {prompt}"
    
    # Prepare the payload for Claude 3
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
        # Invoke Bedrock
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(payload)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Extract JSON from the response
        # Claude might return the JSON with or without markdown
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        music_params = json.loads(content)
        
        # Default values
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
        
        # Combine with defaults
        return {**defaults, **music_params}
        
    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        # Fallback to default parameters
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
    Gets a Spotify access token using the Client Credentials Flow.
    This token only allows searches, not creating playlists.
    """
    auth_url = 'https://accounts.spotify.com/api/token'
    
    # Encode credentials in Base64
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
    Searches for tracks on Spotify based on musical parameters.
    """
    # Use the user's token for searches
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Build search query
    genres = parameters.get('genres', ['pop'])
    genre_query = ' OR '.join([f'genre:"{g}"' for g in genres[:2]])  # Maximum of 2 genres
    
    search_url = 'https://api.spotify.com/v1/search'
    search_params = {
        'q': genre_query,
        'type': 'track',
        'limit': 50,  # Search for more to filter later
        'market': 'US'
    }
    
    try:
        response = requests.get(search_url, headers=headers, params=search_params, timeout=10)
        response.raise_for_status()
        tracks_data = response.json()
        
        # Get track IDs
        track_ids = [track['id'] for track in tracks_data['tracks']['items']]
        
        if not track_ids:
            return []
        
        # Get audio features to filter
        features_url = 'https://api.spotify.com/v1/audio-features'
        features_params = {
            'ids': ','.join(track_ids[:50])  # Maximum of 50 IDs
        }
        
        features_response = requests.get(features_url, headers=headers, params=features_params, timeout=10)
        features_response.raise_for_status()
        audio_features = features_response.json()['audio_features']
        
        # Filter tracks based on parameters
        filtered_tracks = []
        target_energy = parameters.get('energy', 0.5)
        target_danceability = parameters.get('danceability', 0.5)
        target_valence = parameters.get('valence', 0.5)
        min_popularity = parameters.get('popularity', 50)
        limit = min(parameters.get('limit', 20), 50)
        
        for track, features in zip(tracks_data['tracks']['items'], audio_features):
            if features is None:
                continue
            
            # Calculate similarity score
            energy_diff = abs(features['energy'] - target_energy)
            dance_diff = abs(features['danceability'] - target_danceability)
            valence_diff = abs(features['valence'] - target_valence)
            
            score = 1 - (energy_diff + dance_diff + valence_diff) / 3
            
            # Filter by popularity
            if track['popularity'] >= min_popularity:
                filtered_tracks.append({
                    'uri': track['uri'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'score': score
                })
        
        # Sort by score and take the best ones
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
    Creates a new playlist on Spotify and adds the tracks.
    Requires the user's access token (with playlist-modify-public or playlist-modify-private scope).
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get the Spotify user ID from the token
        profile_url = 'https://api.spotify.com/v1/me'
        profile_response = requests.get(profile_url, headers=headers, timeout=10)
        profile_response.raise_for_status()
        spotify_user_id = profile_response.json()['id']
        
        # Create playlist
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
        
        # Add tracks to the playlist
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
    Saves the playlist information to DynamoDB.
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        
        # Get existing playlists for the user
        response = table.get_item(Key={'user_id': user_id})
        
        if 'Item' in response:
            # User exists, add new playlist
            playlists = response['Item'].get('playlists', [])
        else:
            # New user
            playlists = []
        
        # Add new playlist
        playlists.append({
            'playlist_url': playlist_url,
            'prompt': prompt,
            'parameters': parameters,
            'created_at': timestamp
        })
        
        # Save to DynamoDB
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
        # Do not raise exception, the playlist has already been created


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a formatted HTTP response for API Gateway.
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
