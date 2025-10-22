import json
import os
import boto3
from datetime import datetime

# AWS Client Configuration
dynamodb = boto3.resource('dynamodb')

# Environment Variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'AI-DJ-Users')

# DynamoDB Table
table = dynamodb.Table(DYNAMODB_TABLE_NAME)


def create_response(status_code: int, body: dict) -> dict:
    """Helper function to create API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body)
    }


def lambda_handler(event, context):
    """
    Lambda handler to check if a Spotify user is authorized
    - Saves user if first time
    - Checks if approved=true
    - Returns authorization status
    """
    
    # HTTP API v2 format uses different event structure
    http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    
    # Handle OPTIONS preflight
    if http_method == 'OPTIONS':
        return create_response(200, {'message': 'OK'})
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip().lower()
        spotify_id = body.get('spotify_id', '')
        display_name = body.get('display_name', '')
        
        print(f"📧 Checking authorization for: {email}")
        
        is_manual = False
        if not email:
            print(f"⚠️ Missing email, checking for manual entries")
            user_id = f'manual_email#{spotify_id or display_name or "unknown"}'
            is_manual = True
        else:
            user_id = f'spotify_user#{email}'
        
        try:
            # Try to get existing user
            response = table.get_item(Key={'user_id': user_id})
            
            if 'Item' in response:
                # User exists, check if approved
                item = response['Item']
                is_approved = item.get('approved', False)
                
                print(f"🔍 Existing user: {user_id}, approved: {is_approved}")
                response_body = {
                    'authorized': is_approved,
                    'email': email,
                    'message': 'approved' if is_approved else 'awaiting_authorization'
                }
                if is_manual:
                    response_body['manual'] = True
                return create_response(200, response_body)
            else:
                # New user, create entry with approved=false
                timestamp = datetime.utcnow().isoformat()
                item = {
                    'user_id': user_id,
                    'email': email,
                    'spotify_id': spotify_id,
                    'display_name': display_name,
                    'approved': False,
                    'timestamp': timestamp,
                    'last_login': timestamp
                }
                if is_manual:
                    item['source'] = 'manual_email_prompt'
                
                table.put_item(Item=item)
                
                print(f"✅ New user registered: {user_id} (awaiting approval)")
                
                response_body = {
                    'authorized': False,
                    'email': email,
                    'message': 'awaiting_authorization',
                    'first_time': True
                }
                if is_manual:
                    response_body['manual'] = True
                return create_response(200, response_body)
                
        except Exception as db_error:
            print(f"❌ DynamoDB error: {str(db_error)}")
            raise
        
    except json.JSONDecodeError:
        return create_response(400, {
            'error': 'Invalid JSON in request body'
        })
    except Exception as e:
        print(f"❌ Error checking authorization: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })
