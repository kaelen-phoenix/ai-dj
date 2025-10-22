import json
import os
import boto3
import requests
import base64
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from botocore.exceptions import ClientError


# AWS Client Configuration
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Environment Variables
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
# Using Claude Haiku 4.5 - latest and fastest
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')

# DynamoDB Table
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def invoke_bedrock_with_retry(model_id: str, payload: dict, max_retries: int = 3) -> dict:
    """
    Invoke Bedrock with exponential backoff retry logic for throttling
    """
    for attempt in range(max_retries):
        try:
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )
            return json.loads(response['body'].read())
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ThrottlingException' and attempt < max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = (2 ** attempt) * 1
                print(f"[app.py] Throttling detected, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")


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
        
        # Get limit parameter and clamp to avoid timeouts/rate limits
        try:
            limit = int(body.get('limit', 25))
        except Exception:
            limit = 25
        effective_limit = max(1, min(limit, 40))
        
        print(f"Processing request for user_id: {user_id}, prompt: {prompt}, limit: {limit}, effective_limit: {effective_limit}")
        
        # Step 0.5: Use Amazon Q pattern to enhance the prompt before processing
        enhanced_prompt = enhance_prompt_with_q_pattern(prompt)
        print(f"Amazon Q enhanced prompt: {enhanced_prompt}")
        
        # Step 1: Interpret the enhanced prompt with Amazon Bedrock
        music_parameters = interpret_prompt_with_bedrock(enhanced_prompt, effective_limit)
        print(f"Extracted music parameters: {music_parameters}")
        
        # Step 2: Search for tracks on Spotify
        # Ensure we only search up to effective_limit songs
        if isinstance(music_parameters, dict) and isinstance(music_parameters.get('songs'), list):
            music_parameters['songs'] = music_parameters['songs'][:effective_limit]
        tracks = search_spotify_tracks(music_parameters, spotify_access_token)
        
        if not tracks:
            # Return debug info to frontend to help diagnose (model, parameters, songs count)
            return create_response(404, {
                'error': 'No tracks found matching the criteria',
                'model_used': BEDROCK_MODEL_ID,
                'parameters': music_parameters,
                'ai_songs_count': len(music_parameters.get('songs', [])) if isinstance(music_parameters, dict) else 0,
                'timestamp': datetime.utcnow().isoformat()
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
        
        # Successful response with track list
        return create_response(200, {
            'message': 'Playlist created successfully',
            'playlist_url': playlist_url,
            'tracks_count': len(tracks),
            'tracks': tracks,  # Include full track list
            'parameters': music_parameters,
            'model_used': BEDROCK_MODEL_ID,  # Show which model was used
            'timestamp': datetime.utcnow().isoformat(),  # Prevent caching
            'requested_limit': limit,
            'effective_limit': effective_limit
        })
        
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return create_response(500, {
            'error': f'Internal server error: {str(e)}',
            'model_used': BEDROCK_MODEL_ID
        })


def enhance_prompt_with_q_pattern(prompt: str) -> str:
    """
    Use Amazon Q pattern to enhance and expand user prompt with more details
    Makes prompts more specific for better playlist generation
    """
    try:
        q_prompt = f"""Analyze this music request and expand it with relevant details: "{prompt}"

Add specifics about:
- Specific artist examples in that style
- Time period/era if relevant
- Energy level and mood
- Typical occasions for this music
- Language if not specified

Keep it concise (max 2-3 sentences). Be specific with artist names.

Enhanced prompt:"""

        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 200,
            "temperature": 0.7,
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": q_prompt}]}
            ]
        }
        
        response = invoke_bedrock_with_retry(BEDROCK_MODEL_ID, payload, max_retries=1)
        enhanced = response['content'][0]['text'].strip()
        
        print(f"🤖 Amazon Q enhanced: '{prompt}' → '{enhanced}'")
        return enhanced
        
    except Exception as e:
        print(f"⚠️ Amazon Q enhancement failed, using original prompt: {e}")
        return prompt


def interpret_prompt_with_bedrock(prompt: str, limit: int = 25, _retry_if_empty: bool = True, max_retries: int = 4) -> Dict[str, Any]:
    """
    Uses Amazon Bedrock to interpret the user's prompt and suggest specific songs.
    """
    print(f"🤖 Using Bedrock Model: {BEDROCK_MODEL_ID}")
    
    system_prompt = """You are a helpful assistant for creating music playlists. Interpret the user's request and return a strictly filtered list of songs that match ALL inferred constraints, without relying on any hardcoded artist, genre, or country lists.

Return ONLY a JSON object with these keys:
- songs: array of strings with exact format "Song Name - Artist Name"
- playlist_name: string

GENERAL RULES (apply all that match):
1) If the user specifies artist(s) → include ONLY songs by those artist(s).
2) If the user specifies a genre or subgenre → include ONLY songs of that genre/subgenre.
3) If the user specifies a country/region or language → include ONLY artists that match that attribute.
4) Do not substitute adjacent genres or subgenres (e.g., treat related styles as distinct unless the user allows it).
5) For mixed constraints (e.g., genre + country + artist), respect ALL simultaneously.
6) If uncertain whether a song satisfies ALL constraints, EXCLUDE it.

VALIDATION CHECKLIST (must pass for every song):
- Check that the artist and song align with the requested genre/subgenre (if specified).
- Check that the artist's origin or language matches the requested country/region/language (if specified).
- Remove any candidate that fails any constraint or seems doubtful.

Output requirements:
- Only JSON, no explanations, no markdown, no comments.
- Use real, popular songs available on Spotify.
"""

    # Add timestamp to prevent caching
    import time
    request_id = int(time.time() * 1000)
    
    user_message = f"""[Request ID: {request_id}] Create a playlist with {limit} songs based on: "{prompt}"

Process to follow (no prose in output):
1) Extract constraints explicitly stated by the user (artist(s), genre/subgenre, country/region, language, era, mood, etc.).
2) Propose candidates and FILTER OUT anything that violates ANY constraint.
3) Validate each remaining song against ALL constraints. If uncertain, exclude it.
4) Return ONLY strict JSON with keys: songs, playlist_name. No markdown, no extra text.

Now create the playlist with {limit} songs:"""
    
    # Prepare the payload for Anthropic Messages API (Bedrock)
    # Calculate required tokens based on limit (each song ~20 tokens)
    # For 100 songs we need ~2500 tokens minimum
    required_tokens = max(800, limit * 25 + 500)
    
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": min(required_tokens, 4096),  # Cap at model limit
        "temperature": 0.7,
        "system": system_prompt,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_message}
                ]
            }
        ]
    }
    
    try:
        # Invoke Bedrock with retry logic
        response_body = invoke_bedrock_with_retry(BEDROCK_MODEL_ID, payload, max_retries=max_retries)
        print(f"Bedrock raw response keys: {list(response_body.keys())}")
        if isinstance(response_body, dict):
            print(f"Bedrock meta: model={response_body.get('model')} stop_reason={response_body.get('stop_reason')}")

        # Try multiple ways to extract text content
        content = None
        try:
            if isinstance(response_body.get('content'), list) and response_body['content']:
                # Anthropic messages format
                content = response_body['content'][0].get('text') or response_body['content'][0].get('content')
        except Exception:
            pass

        # Some providers return 'output_text' directly
        if not content and isinstance(response_body.get('output_text'), str):
            content = response_body['output_text']

        # Fallback: if body itself is a JSON with expected fields
        if not content and ('songs' in response_body or 'playlist_name' in response_body):
            music_params = {
                'songs': response_body.get('songs', []),
                'playlist_name': response_body.get('playlist_name', 'AI DJ Playlist')
            }
            return music_params

        if not content and isinstance(response_body, dict):
            # Last resort: stringify
            content = json.dumps(response_body)

        # Extract JSON from free-text content
        text = content or ''
        # First try direct JSON
        music_params = None
        try:
            music_params = json.loads(text)
        except Exception:
            # Strip markdown fences
            if '```json' in text:
                text = text.split('```json', 1)[1].split('```', 1)[0].strip()
            elif '```' in text:
                text = text.split('```', 1)[1].split('```', 1)[0].strip()
            # Try to locate first JSON object heuristically
            if not (text.strip().startswith('{') and text.strip().endswith('}')):
                # find first '{' and last '}'
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1 and end > start:
                    text = text[start:end+1]
            try:
                music_params = json.loads(text)
            except Exception as ex:
                print(f"Failed to parse AI content as JSON: {str(ex)} | content preview: {str((content or '') )[:400]}")
                music_params = {}

        # Ensure required fields
        if 'songs' not in music_params:
            music_params['songs'] = []
        if 'playlist_name' not in music_params:
            music_params['playlist_name'] = 'AI DJ Playlist'

        # If no songs were produced, do a single JSON-enforcing retry
        if _retry_if_empty and (not isinstance(music_params.get('songs'), list) or len(music_params.get('songs', [])) == 0):
            print("No songs in AI response. Retrying with strict JSON-only instruction...")
            strict_system = """You generate playlists. Return ONLY valid minified JSON, no markdown, no comments, no prose.
Keys: songs (array of strings "Song - Artist"), playlist_name (string). Do not add extra keys. Do not wrap in backticks. Do not explain.
If the user asked for genre or country, pick real, popular songs that exist on Spotify."""
            strict_user = f"""Create a playlist with {limit} songs based on: \"{prompt}\". Return exactly:
{{"songs": ["Song - Artist"], "playlist_name": "Name"}} and nothing else."""

            strict_payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 800,
                "temperature": 0.3,
                "system": strict_system,
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": strict_user}]}
                ]
            }

            try:
                strict_body = invoke_bedrock_with_retry(BEDROCK_MODEL_ID, strict_payload, max_retries=max_retries)
                strict_text = None
                if isinstance(strict_body.get('content'), list) and strict_body['content']:
                    strict_text = strict_body['content'][0].get('text') or strict_body['content'][0].get('content')
                if not strict_text and isinstance(strict_body.get('output_text'), str):
                    strict_text = strict_body['output_text']
                if not strict_text:
                    strict_text = json.dumps(strict_body)
                # Try direct JSON first, then remove fences if any
                try:
                    strict_params = json.loads(strict_text)
                except Exception:
                    if '```json' in strict_text:
                        strict_text = strict_text.split('```json', 1)[1].split('```', 1)[0].strip()
                    elif '```' in strict_text:
                        strict_text = strict_text.split('```', 1)[1].split('```', 1)[0].strip()
                    strict_params = json.loads(strict_text)

                if 'songs' not in strict_params:
                    strict_params['songs'] = []
                if 'playlist_name' not in strict_params:
                    strict_params['playlist_name'] = 'AI DJ Playlist'

                music_params = strict_params
            except Exception as rex:
                print(f"Retry failed to produce songs: {str(rex)}")

        return music_params
        
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
    Searches for specific songs on Spotify based on AI suggestions.
    Returns track details including name, artist, and URI.
    """
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    songs = parameters.get('songs', [])
    
    if not songs:
        print("No songs suggested by AI")
        return []
    
    print(f"Searching for {len(songs)} specific songs suggested by AI")
    
    # Search for each specific song
    search_url = 'https://api.spotify.com/v1/search'
    found_tracks = []
    
    for song in songs:
        try:
            print(f"Searching for: {song}")
            
            # Search for the exact song
            search_params = {
                'q': song,
                'type': 'track',
                'limit': 1,  # Get only the best match
                'market': 'US'
            }
            
            response = requests.get(search_url, headers=headers, params=search_params, timeout=10)
            response.raise_for_status()
            tracks_data = response.json()
            
            # Get the first (best) result
            if tracks_data['tracks']['items']:
                track = tracks_data['tracks']['items'][0]
                found_tracks.append({
                    'uri': track['uri'],
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'popularity': track['popularity'],
                    'id': track['id'],
                    'album': track['album']['name'],
                    'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None
                })
                print(f"✓ Found: {track['name']} - {track['artists'][0]['name']}")
            else:
                print(f"✗ Not found: {song}")
            
        except Exception as e:
            print(f"Error searching for '{song}': {str(e)}")
            continue
    
    print(f"Successfully found {len(found_tracks)} out of {len(songs)} songs")
    
    return found_tracks


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
