"""
Lambda handler for Amazon Q Business - Music knowledge base
Provides expert knowledge about music genres, artists, history, and recommendations
"""

import json
import os
import boto3
from typing import Dict, Any, List
from datetime import datetime

# AWS Clients
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
# Amazon Q Business client (if configured)
try:
    q_business = boto3.client('qbusiness', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
except Exception:
    q_business = None

# Environment Variables
Q_APPLICATION_ID = os.environ.get('Q_APPLICATION_ID')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID', 'us.anthropic.claude-haiku-4-5-20251001-v1:0')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main handler for music knowledge queries
    """
    try:
        body = json.loads(event.get('body', '{}'))
        user_id = body.get('user_id')
        query = body.get('query')
        
        if not user_id or not query:
            return create_response(400, {
                'error': 'Missing required parameters: user_id and query'
            })
        
        print(f"Knowledge query from {user_id}: {query}")
        
        # Try Amazon Q Business first if configured
        if Q_APPLICATION_ID and q_business:
            response = query_amazon_q(Q_APPLICATION_ID, user_id, query)
        else:
            # Fallback: Use Bedrock with music knowledge
            response = query_with_bedrock_knowledge(query)
        
        return create_response(200, response)
        
    except Exception as e:
        print(f"Error in knowledge handler: {str(e)}")
        return create_response(500, {
            'error': f'Internal server error: {str(e)}'
        })


def query_amazon_q(app_id: str, user_id: str, query: str) -> Dict[str, Any]:
    """
    Query Amazon Q Business application
    """
    try:
        response = q_business.chat_sync(
            applicationId=app_id,
            userId=user_id,
            userMessage=query
        )
        
        # Extract answer from Q response
        answer = ""
        sources = []
        
        if 'systemMessage' in response:
            answer = response['systemMessage']
        
        if 'sourceAttributions' in response:
            for source in response['sourceAttributions']:
                sources.append({
                    'title': source.get('title', ''),
                    'url': source.get('url', ''),
                    'snippet': source.get('snippet', '')
                })
        
        return {
            'answer': answer,
            'sources': sources,
            'source_type': 'amazon_q',
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error querying Amazon Q: {str(e)}")
        raise


def query_with_bedrock_knowledge(query: str) -> Dict[str, Any]:
    """
    Fallback: Use Bedrock with embedded music knowledge
    """
    system_prompt = """You are a music expert with deep knowledge of:
- Music genres, subgenres, and their characteristics
- Artist histories, influences, and discographies
- Music theory and composition
- Cultural and historical context of different music styles
- Current trends and emerging artists
- Playlist curation best practices

Provide accurate, detailed, and helpful information about music.
If you don't know something, say so rather than making it up.
"""
    
    user_message = f"""User question about music: {query}

Provide a comprehensive, accurate answer. Include:
1. Direct answer to the question
2. Relevant context or background
3. Examples if applicable
4. Suggestions for further exploration

Format as JSON with keys: answer (string), context (string), examples (array), suggestions (array)"""
    
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "temperature": 0.3,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": user_message}]}
        ]
    }
    
    try:
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Try to parse as JSON
        try:
            knowledge_data = json.loads(content)
        except:
            # Extract JSON if wrapped
            if '```json' in content:
                content = content.split('```json', 1)[1].split('```', 1)[0].strip()
            elif '```' in content:
                content = content.split('```', 1)[1].split('```', 1)[0].strip()
            
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                knowledge_data = json.loads(content[start:end])
            else:
                # Fallback: return as plain text
                knowledge_data = {
                    'answer': content,
                    'context': '',
                    'examples': [],
                    'suggestions': []
                }
        
        return {
            **knowledge_data,
            'source_type': 'bedrock_knowledge',
            'model_used': BEDROCK_MODEL_ID,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        print(f"Error querying Bedrock: {str(e)}")
        raise


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
