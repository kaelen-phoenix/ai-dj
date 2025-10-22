import json
import os
import boto3
from datetime import datetime
from decimal import Decimal

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
    Lambda handler for access requests
    Saves user email requests to DynamoDB for manual whitelist approval
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
        user_agent = body.get('user_agent', 'Unknown')
        
        if not email:
            return create_response(400, {
                'error': 'Email is required'
            })
        
        # Validate email format
        if '@' not in email or '.' not in email.split('@')[1]:
            return create_response(400, {
                'error': 'Invalid email format'
            })
        
        # Create timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Save to DynamoDB with special prefix for access requests
        table.put_item(
            Item={
                'user_id': f'ACCESS_REQUEST#{email}',
                'timestamp': timestamp,
                'email': email,
                'user_agent': user_agent,
                'status': 'pending',
                'request_type': 'spotify_whitelist',
                'notes': f'Access request submitted on {timestamp}'
            }
        )
        
        print(f"✅ Access request saved: {email}")
        
        return create_response(200, {
            'message': 'Access request submitted successfully',
            'email': email,
            'status': 'pending',
            'note': 'You will be notified once approved'
        })
        
    except json.JSONDecodeError:
        return create_response(400, {
            'error': 'Invalid JSON in request body'
        })
    except Exception as e:
        print(f"❌ Error processing access request: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })
