"""
Lambda handler for Amazon Nova Act - Image/Video-based playlist generation
Analyzes images or videos to detect mood/vibe and creates matching playlists
"""

import json
import os
import boto3
import base64
import requests
from typing import Dict, Any, List
from datetime import datetime

# AWS Clients
dynamodb = boto3.resource('dynamodb')
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
s3 = boto3.client('s3')

# Environment Variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')
# Nova Act model for vision
NOVA_MODEL_ID = os.environ.get('NOVA_MODEL_ID', 'us.amazon.nova-lite-v1:0')

table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main handler for image/video-based playlist generation
    """
    try:
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        image_data = body.get('image_data')  # Base64 encoded image
        image_url = body.get('image_url')     # Or URL to image
        spotify_access_token = body.get('spotify_access_token')
        limit = int(body.get('limit', 25))
        
        if not user_id:
            return create_response(400, {'error': 'Missing user_id'})
        
        if not spotify_access_token:
            return create_response(400, {'error': 'Missing spotify_access_token'})
        
        if not image_data and not image_url:
            return create_response(400, {'error': 'Missing image_data or image_url'})
        
        print(f"Processing image for user: {user_id}")
        
        # Step 1: Analyze image with Nova Act
        mood_analysis = analyze_image_with_nova(image_data, image_url)
        print(f"Mood analysis: {mood_analysis}")
        
        # Step 2: Generate specific song suggestions based on image analysis
        # Instead of just a prompt, get actual song suggestions from AI
        playlist_prompt = mood_analysis.get('playlist_prompt', 'Energetic and upbeat music')
        
        # Step 3: Get AI to suggest SPECIFIC songs based on the image analysis
        from app import interpret_prompt_with_bedrock, search_spotify_tracks, create_spotify_playlist, save_playlist_to_dynamodb
        
        # Use the detailed prompt to get specific song suggestions
        music_parameters = interpret_prompt_with_bedrock(playlist_prompt, limit)
        
        # Search for the specific songs suggested by AI
        tracks = search_spotify_tracks(music_parameters, spotify_access_token)
        
        if not tracks:
            return create_response(404, {
                'error': 'No tracks found',
                'mood_analysis': mood_analysis,
                'generated_prompt': playlist_prompt
            })
        
        playlist_url = create_spotify_playlist(
            user_id=user_id,
            playlist_name=music_parameters.get('playlist_name', f"AI DJ - {mood_analysis.get('mood', 'Vibe')} Mix"),
            track_uris=[track['uri'] for track in tracks],
            access_token=spotify_access_token
        )
        
        # Save with image metadata
        save_playlist_to_dynamodb(user_id, playlist_url, playlist_prompt, {
            **music_parameters,
            'source': 'image_analysis',
            'mood_analysis': mood_analysis
        })
        
        return create_response(200, {
            'message': 'Playlist created from image analysis',
            'playlist_url': playlist_url,
            'tracks_count': len(tracks),
            'tracks': tracks,
            'mood_analysis': mood_analysis,
            'generated_prompt': playlist_prompt,
            'model_used': f'{NOVA_MODEL_ID} + {BEDROCK_MODEL_ID}'
        })
        
    except Exception as e:
        print(f"Error in image handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return create_response(500, {
            'error': f'Internal server error: {str(e)}'
        })


def analyze_image_with_nova(image_data: str = None, image_url: str = None) -> Dict[str, Any]:
    """
    Analyze image using Amazon Nova Act to detect mood, scene, and vibe
    """
    try:
        # Prepare image content
        if image_url:
            # Download image from URL
            response = requests.get(image_url, timeout=10)
            image_bytes = response.content
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        elif image_data:
            # Use provided base64 data
            image_b64 = image_data
        else:
            raise ValueError("No image provided")
        
        # Detect media type and format
        media_type = "image/jpeg"
        image_format = "jpeg"
        
        if image_b64.startswith('/9j/'):
            media_type = "image/jpeg"
            image_format = "jpeg"
        elif image_b64.startswith('iVBORw'):
            media_type = "image/png"
            image_format = "png"
        elif image_b64.startswith('R0lG'):
            media_type = "image/gif"
            image_format = "gif"
        elif image_b64.startswith('UklGR'):
            # WebP format
            media_type = "image/webp"
            image_format = "webp"
        
        # Prepare Nova Act request
        system_prompt = """You are an expert at analyzing images to create perfect music playlists.

IMPORTANT RULES:
1. If you see a PERSON/CELEBRITY/ARTIST: Identify them and create a playlist of THEIR music or similar artists
2. If you see visual themes (demons, skulls, dark imagery): Match with appropriate genre (heavy metal, rock, etc.)
3. If you see a scene/mood: Match music to that atmosphere

Analyze the image and provide:
- detected_person: name of person/artist if recognizable (or null)
- visual_theme: what you see (e.g., "dark demonic imagery", "concert photo", "sunset beach")
- mood: primary emotional tone
- energy_level: 0-1 (0=calm, 1=energetic)
- valence: 0-1 (0=sad, 1=happy)
- suggested_genres: array of music genres that match
- playlist_prompt: DETAILED prompt for playlist generation

EXAMPLES:
- Image of Christina Aguilera → playlist_prompt: "Pop hits from Christina Aguilera including Genie in a Bottle, Beautiful, Fighter, plus similar artists like Britney Spears (Toxic, Oops I Did It Again), Pink (So What, Just Give Me a Reason), Beyoncé (Crazy in Love, Halo)"
- Image of demon/skull → playlist_prompt: "Heavy metal and hard rock with dark themes: Slayer (Raining Blood, Angel of Death), Metallica (Master of Puppets, Enter Sandman), Black Sabbath (Paranoid, Iron Man), Judas Priest, Iron Maiden"
- Image of Minion → playlist_prompt: "Fun, upbeat, playful pop music perfect for kids and families: Pharrell Williams (Happy), Justin Timberlake (Can't Stop the Feeling), Meghan Trainor (All About That Bass), Mark Ronson (Uptown Funk)"
- Image of beach sunset → playlist_prompt: "Relaxing chill music perfect for sunset: tropical house like Kygo (Firestone, Stole the Show), acoustic vibes, Jack Johnson (Better Together), Norah Jones (Don't Know Why)"

Be VERY SPECIFIC with artist names and song titles. The more specific, the better the playlist will be.

Return JSON format."""
        
        user_message = """Analyze this image carefully and be VERY SPECIFIC:

1. Is there a recognizable person/celebrity/artist? If yes, identify them BY NAME.
2. What is the visual theme or mood?
3. What SPECIFIC SONGS and ARTISTS would match this image?

CRITICAL: In your playlist_prompt, include:
- SPECIFIC artist names (e.g., "Pharrell Williams", "Metallica", "Christina Aguilera")
- SPECIFIC song titles when possible (e.g., "Happy", "Master of Puppets", "Beautiful")
- Multiple artists and songs, not just genres

Example good prompt: "Pharrell Williams (Happy), Justin Timberlake (Can't Stop the Feeling), Meghan Trainor (All About That Bass)"
Example bad prompt: "upbeat pop music" (too generic)

Be as specific as possible with artist and song names."""
        
        # Call Nova Act (multimodal model)
        # NOTE: Nova models don't use 'max_tokens', they use 'inferenceConfig'
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "image": {
                                "format": image_format,  # jpeg, png, gif, webp
                                "source": {
                                    "bytes": image_b64
                                }
                            }
                        },
                        {
                            "text": f"{system_prompt}\n\n{user_message}"
                        }
                    ]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 800,
                "temperature": 0.5
            }
        }
        
        response = bedrock_runtime.invoke_model(
            modelId=NOVA_MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        print(f"Nova response body: {json.dumps(response_body)[:500]}")
        
        # Nova response format: {"output": {"message": {"content": [{"text": "..."}]}}}
        if 'output' in response_body and 'message' in response_body['output']:
            content = response_body['output']['message']['content'][0]['text']
        elif 'content' in response_body:
            # Fallback to Claude format
            content = response_body['content'][0]['text']
        else:
            raise Exception(f"Unexpected Nova response format: {list(response_body.keys())}")
        
        print(f"Nova content: {content[:500]}")
        
        # Parse JSON from response
        try:
            # Try direct JSON parse
            analysis = json.loads(content)
            print(f"Successfully parsed JSON: {analysis}")
        except Exception as parse_error:
            print(f"Failed to parse as direct JSON: {parse_error}")
            # Extract JSON from markdown
            if '```json' in content:
                content = content.split('```json', 1)[1].split('```', 1)[0].strip()
            elif '```' in content:
                content = content.split('```', 1)[1].split('```', 1)[0].strip()
            
            # Find JSON object
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                try:
                    analysis = json.loads(content[start:end])
                    print(f"Successfully extracted JSON: {analysis}")
                except Exception as extract_error:
                    print(f"Failed to extract JSON: {extract_error}")
                    print(f"Content was: {content[start:end][:500]}")
                    # Fallback
                    analysis = {
                        'detected_person': None,
                        'visual_theme': 'Unknown',
                        'mood': 'energetic',
                        'energy_level': 0.7,
                        'valence': 0.7,
                        'suggested_genres': ['pop', 'rock'],
                        'playlist_prompt': 'Energetic and upbeat music'
                    }
            else:
                print(f"No JSON object found in content")
                # Fallback
                analysis = {
                    'detected_person': None,
                    'visual_theme': 'Unknown',
                    'mood': 'energetic',
                    'energy_level': 0.7,
                    'valence': 0.7,
                    'suggested_genres': ['pop', 'rock'],
                    'playlist_prompt': 'Energetic and upbeat music'
                }
        
        return analysis
        
    except Exception as e:
        print(f"Error analyzing image with Nova: {str(e)}")
        # Return default analysis
        return {
            'detected_person': None,
            'visual_theme': 'Unknown',
            'mood': 'energetic',
            'energy_level': 0.7,
            'valence': 0.7,
            'suggested_genres': ['pop', 'rock'],
            'playlist_prompt': 'Energetic and upbeat music',
            'error': str(e)
        }


def create_response(status_code: int, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a formatted HTTP response for API Gateway
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
