"""
Lambda handler for Bedrock AgentCore - Conversational playlist creation
Allows multi-turn conversations to refine playlists iteratively
"""

import json
import os
import boto3
import sys
import time
from typing import Dict, Any, List
from datetime import datetime
from botocore.exceptions import ClientError

# Add lambda_src to path to import app functions
sys.path.insert(0, os.path.dirname(__file__))

# AWS Clients
dynamodb = boto3.resource('dynamodb')
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# Environment Variables
AGENT_ID = os.environ.get('BEDROCK_AGENT_ID')
AGENT_ALIAS_ID = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'TSTALIASID')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')
SPOTIFY_CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')

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
                print(f"Throttling detected, waiting {wait_time}s before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main handler for AgentCore conversational interface
    """
    try:
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        message = body.get('message')
        session_id = body.get('session_id')
        spotify_token = body.get('spotify_access_token')
        limit = int(body.get('limit', 25))
        
        if not user_id or not message:
            return create_response(400, {'error': 'Missing user_id or message'})
        
        if not spotify_token:
            return create_response(400, {'error': 'Missing spotify_access_token'})
        
        print(f"Agent conversation - user: {user_id}, session: {session_id}, message: {message}")
        
        # If we have an agent configured, use it
        if AGENT_ID:
            response = invoke_bedrock_agent(
                agent_id=AGENT_ID,
                agent_alias_id=AGENT_ALIAS_ID,
                session_id=session_id or f"session-{user_id}-{datetime.now().timestamp()}",
                prompt=message,
                user_id=user_id,
                spotify_token=spotify_token
            )
        else:
            # Fallback: simulate agent behavior with direct Bedrock calls
            response = simulate_agent_conversation(
                message=message,
                session_id=session_id or f"session-{user_id}-{datetime.now().timestamp()}",
                user_id=user_id,
                spotify_token=spotify_token,
                limit=limit
            )
        
        return create_response(200, response)
        
    except Exception as e:
        print(f"Error in agent handler: {str(e)}")
        return create_response(500, {
            'error': f'Internal server error: {str(e)}'
        })


def invoke_bedrock_agent(
    agent_id: str,
    agent_alias_id: str,
    session_id: str,
    prompt: str,
    user_id: str,
    spotify_token: str
) -> Dict[str, Any]:
    """
    Invoke Bedrock Agent with session management
    """
    try:
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=session_id,
            inputText=prompt,
            sessionState={
                'sessionAttributes': {
                    'user_id': user_id,
                    'spotify_token': spotify_token
                }
            }
        )
        
        # Parse streaming response
        agent_response = ""
        for event in response.get('completion', []):
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    agent_response += chunk['bytes'].decode('utf-8')
        
        return {
            'message': agent_response,
            'session_id': session_id,
            'agent_used': True
        }
        
    except Exception as e:
        print(f"Error invoking Bedrock Agent: {str(e)}")
        raise


def simulate_agent_conversation(
    message: str,
    session_id: str,
    user_id: str,
    spotify_token: str,
    limit: int = 25
) -> Dict[str, Any]:
    """
    Simulate agent behavior using direct Bedrock calls with conversation history
    This is a fallback when Agent is not configured
    """
    # Get conversation history from DynamoDB
    history = get_conversation_history(session_id)
    
    # Build context-aware prompt
    system_prompt = """You are AI DJ, a helpful music assistant that creates Spotify playlists.
You can have multi-turn conversations to understand user preferences and refine playlists.

IMPORTANT: Always respond in the SAME LANGUAGE the user is using. If they speak Spanish, respond in Spanish. If English, respond in English.

Available actions:
1. Ask clarifying questions about music preferences (genre, mood, energy, artists, etc.)
2. Suggest playlist ideas based on conversation
3. When user confirms they want to create the playlist, generate a detailed music prompt

When user is ready to create a playlist, respond with:
READY_TO_CREATE: [detailed prompt describing the music style, mood, genres, energy level, etc.]

Examples:
User (English): "Yes, create it!"
Response: READY_TO_CREATE: Energetic rock music with high energy, featuring artists like Foo Fighters and Queens of the Stone Age, perfect for working out

User (Spanish): "Sí, creala!"
Response: READY_TO_CREATE: Música rock energética con alta energía, con artistas como Foo Fighters y Queens of the Stone Age, perfecta para entrenar

Otherwise, respond naturally to continue the conversation and gather more preferences."""
    
    # Check if user wants to create playlist (keywords)
    create_keywords = ['si', 'sí', 'yes', 'dale', 'ok', 'creala', 'créala', 'create', 'hazla', 'hacela', 'go', 'adelante']
    user_wants_to_create = any(keyword == message.lower().strip() or keyword in message.lower().split() for keyword in create_keywords)
    
    # If user wants to create, skip ALL Bedrock calls for conversation
    if user_wants_to_create and len(history) > 0:
        # Build playlist prompt from ALL user messages
        conversation_summary = " ".join([
            f"{h['content']}"
            for h in history if h['role'] == 'user'  # ALL user messages
        ])
        
        playlist_prompt = conversation_summary
        print(f"✅ DIRECT CREATION - Skipping Bedrock conversation. Prompt: {playlist_prompt[:100]}...")
        
        assistant_message = f"READY_TO_CREATE: {playlist_prompt}"
        save_conversation_turn(session_id, message, "¡Creando tu playlist!")
    else:
        # Use Amazon Q pattern to generate intelligent follow-up questions
        # based on conversation context
        if len(history) == 0:
            assistant_message = "¡Hola! Describime qué tipo de música te gustaría y voy a hacerte algunas preguntas para crear la playlist perfecta."
        else:
            # Use Bedrock with Amazon Q pattern to generate contextual questions
            conversation_summary = " ".join([
                f"{h['content']}"
                for h in history[-3:] if h['role'] == 'user'
            ])
            
            q_prompt = f"""Based on this music request: "{conversation_summary}"

Generate ONE intelligent follow-up question to refine the playlist. Ask about:
- Specific artists they like in that genre
- Time period or era (80s, 90s, modern, etc.)
- Energy level (chill, energetic, intense)
- Mood or occasion (workout, study, party, relax)
- Language preference
- Any artists to avoid

Be conversational and natural in Spanish. End with: "O decime 'si' si ya estás listo para crear la playlist."

Question:"""

            try:
                # Quick call to Bedrock for intelligent question (Amazon Q pattern)
                q_payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 150,
                    "temperature": 0.8,
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": q_prompt}]}
                    ]
                }
                
                q_response = invoke_bedrock_with_retry(
                    model_id=os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0'),
                    payload=q_payload,
                    max_retries=1  # Quick retry only
                )
                
                assistant_message = q_response['content'][0]['text'].strip()
                print(f"🤖 Amazon Q generated question: {assistant_message}")
                
            except Exception as e:
                print(f"⚠️ Q pattern failed, using fallback: {e}")
                # Fallback questions if Bedrock fails
                fallback_questions = [
                    "¿Qué artistas o bandas te gustan de ese estilo? O decime 'si' si ya estás listo.",
                    "¿De qué época preferís la música? ¿Clásicos o más reciente? O decime 'si' para crear.",
                    "¿Qué energía buscás? ¿Tranquilo o más intenso? O decime 'si' cuando quieras."
                ]
                assistant_message = fallback_questions[len(history) % 3]
        
        # Save to conversation history
        save_conversation_turn(session_id, message, assistant_message)
    
    # Check if we should create playlist
    if 'READY_TO_CREATE:' in assistant_message:
        # Extract the prompt after READY_TO_CREATE:
        prompt_start = assistant_message.find('READY_TO_CREATE:') + len('READY_TO_CREATE:')
        playlist_prompt = assistant_message[prompt_start:].strip()
        
        # Import functions from app.py to create the actual playlist
        try:
            import app
            
            print(f"Creating playlist with prompt: {playlist_prompt}, limit: {limit}")
            
            # Generate playlist using the same logic as the main handler
            music_parameters = app.interpret_prompt_with_bedrock(playlist_prompt, limit, max_retries=3)
            print(f"Music parameters: {music_parameters}")
            
            if not music_parameters or not music_parameters.get('songs'):
                return {
                    'message': "Estoy teniendo problemas técnicos para generar la playlist en este momento (demasiadas solicitudes). Por favor, intentá de nuevo en unos segundos. 🙏",
                    'session_id': session_id,
                    'agent_used': False,
                    'conversation_mode': True
                }
            
            tracks = app.search_spotify_tracks(music_parameters, spotify_token)
            print(f"Found {len(tracks)} tracks")
            
            if tracks:
                try:
                    print(f"Creating Spotify playlist with {len(tracks)} tracks...")
                    playlist_url = app.create_spotify_playlist(
                        user_id=user_id,
                        playlist_name=music_parameters.get('playlist_name', 'AI DJ - Chat Playlist'),
                        track_uris=[track['uri'] for track in tracks],
                        access_token=spotify_token
                    )
                    print(f"✅ Playlist created successfully: {playlist_url}")
                    
                    # Return success with playlist info
                    return {
                        'message': f"✅ ¡Playlist creada exitosamente! Agregué {len(tracks)} canciones basadas en nuestra conversación.",
                        'session_id': session_id,
                        'agent_used': False,
                        'conversation_mode': True,
                        'playlist_created': True,
                        'playlist_url': playlist_url,
                        'tracks_count': len(tracks),
                        'tracks': tracks[:10]  # First 10 tracks for preview
                    }
                except Exception as playlist_error:
                    print(f"❌ Error creating Spotify playlist: {str(playlist_error)}")
                    import traceback
                    traceback.print_exc()
                    return {
                        'message': f"Encontré {len(tracks)} canciones perfectas, pero hubo un error al crear la playlist en Spotify. Por favor, intentá de nuevo.",
                        'session_id': session_id,
                        'agent_used': False,
                        'conversation_mode': True,
                        'error': str(playlist_error)
                    }
            else:
                return {
                    'message': "No encontré suficientes canciones que coincidan con esas preferencias. ¿Podrías describirlo de otra manera?",
                    'session_id': session_id,
                    'agent_used': False,
                    'conversation_mode': True
                }
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error creating playlist from chat: {str(e)}")
            print(f"Full traceback: {error_details}")
            return {
                'message': f"Entendí que querés crear la playlist, pero encontré un error técnico. Por favor intentá de nuevo o describí la música de otra forma.",
                'session_id': session_id,
                'agent_used': False,
                'conversation_mode': True,
                'error_detail': str(e)
            }
    
    # Normal conversation response
    result = {
        'message': assistant_message,
        'session_id': session_id,
        'agent_used': False,
        'conversation_mode': True
    }
    
    return result


def get_conversation_history(session_id: str) -> List[Dict[str, str]]:
    """
    Retrieve conversation history from DynamoDB
    """
    try:
        response = table.get_item(Key={'user_id': f'session#{session_id}'})
        if 'Item' in response:
            return response['Item'].get('history', [])
        return []
    except Exception as e:
        print(f"Error getting conversation history: {str(e)}")
        return []


def save_conversation_turn(session_id: str, user_message: str, assistant_message: str):
    """
    Save conversation turn to DynamoDB
    """
    try:
        history = get_conversation_history(session_id)
        history.append({'role': 'user', 'content': user_message})
        history.append({'role': 'assistant', 'content': assistant_message})
        
        # Keep only last 20 messages
        if len(history) > 20:
            history = history[-20:]
        
        table.put_item(
            Item={
                'user_id': f'session#{session_id}',
                'history': history,
                'last_updated': datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        print(f"Error saving conversation: {str(e)}")


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
