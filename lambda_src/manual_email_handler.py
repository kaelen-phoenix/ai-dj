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
    Lambda handler to store manual email submissions
    """
    http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')

    if http_method == 'OPTIONS':
        return create_response(200, {'message': 'OK'})

    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip().lower()
        source = body.get('source', 'manual_email_prompt')
        spotify_id = body.get('spotify_id')
        user_agent = body.get('user_agent')
        timestamp = body.get('timestamp') or datetime.utcnow().isoformat()
        session_id = body.get('session_id')
        display_name = body.get('display_name')

        if not email:
            return create_response(400, {
                'error': 'Bad request',
                'message': 'Email is required'
            })

        user_id = f'spotify_user#{email}'

        item = {
            'user_id': user_id,
            'email': email,
            'source': source,
            'spotify_id': spotify_id,
            'user_agent': user_agent,
            'timestamp': timestamp,
            'approved': False,
            'status': 'pending_manual_approval'
        }

        if session_id:
            item['session_id'] = session_id
        if display_name:
            item['display_name'] = display_name

        table.put_item(Item=item)

        return create_response(200, {
            'message': 'Manual email registered',
            'email': email,
            'status': 'pending'
        })

    except json.JSONDecodeError:
        return create_response(400, {'error': 'Invalid JSON in request body'})
    except Exception as e:
        print(f"❌ Error storing manual email: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })
