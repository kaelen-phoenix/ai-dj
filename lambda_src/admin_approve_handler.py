import json
import os
import boto3
from datetime import datetime

# AWS Client Configuration
dynamodb = boto3.resource('dynamodb')

# Environment Variables
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'AI-DJ-Users')
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    raise ValueError('ADMIN_USERNAME and ADMIN_PASSWORD environment variables must be set')

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
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,x-admin-user,x-admin-pass'
        },
        'body': json.dumps(body)
    }


def lambda_handler(event, context):
    """
    Lambda handler to approve/reject users
    Updates the 'approved' field in DynamoDB
    """
    
    # HTTP API v2 format uses different event structure
    http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    
    # Handle OPTIONS preflight
    if http_method == 'OPTIONS':
        return create_response(200, {'message': 'OK'})
    
    # Simple authentication check
    # Headers can come in different cases
    headers = event.get('headers', {})
    headers_lower = {k.lower(): v for k, v in headers.items()}
    auth_user = headers_lower.get('x-admin-user', '')
    auth_pass = headers_lower.get('x-admin-pass', '')
    
    # Validate credentials
    if auth_user != ADMIN_USERNAME or auth_pass != ADMIN_PASSWORD:
        return create_response(401, {
            'error': 'Unauthorized',
            'message': 'Invalid admin credentials'
        })
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip().lower()
        approved = body.get('approved', False)
        
        if not email:
            return create_response(400, {
                'error': 'Email is required'
            })
        
        # Update item in DynamoDB
        user_id = f'spotify_user#{email}'
        
        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET approved = :approved, last_updated = :timestamp',
            ExpressionAttributeValues={
                ':approved': approved,
                ':timestamp': datetime.utcnow().isoformat()
            },
            ReturnValues='ALL_NEW'
        )
        
        print(f"✅ User {email} approval status updated to: {approved}")
        
        return create_response(200, {
            'message': 'Approval status updated',
            'email': email,
            'approved': approved
        })
        
    except json.JSONDecodeError:
        return create_response(400, {
            'error': 'Invalid JSON in request body'
        })
    except Exception as e:
        print(f"❌ Error updating approval status: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })
