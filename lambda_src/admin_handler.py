import json
import os
import boto3
from boto3.dynamodb.conditions import Attr
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
            'Access-Control-Allow-Methods': 'GET,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,x-admin-user,x-admin-pass'
        },
        'body': json.dumps(body)
    }


def lambda_handler(event, context):
    """
    Lambda handler for admin requests
    Returns all access requests from DynamoDB
    """
    
    # HTTP API v2 format uses different event structure
    # Get method from either format (REST API or HTTP API v2)
    http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
    
    # Log the incoming event for debugging
    print(f"📥 Event: httpMethod={http_method}, path={event.get('path', 'N/A')}")
    print(f"📋 Headers: {event.get('headers', {})}")
    
    # Handle OPTIONS preflight
    if http_method == 'OPTIONS':
        print("✅ Handling OPTIONS request")
        return create_response(200, {'message': 'OK'})
    
    # Simple authentication check (username/password in headers)
    # Headers can come in different cases
    headers = event.get('headers', {})
    # Convert all keys to lowercase for case-insensitive access
    headers_lower = {k.lower(): v for k, v in headers.items()}
    auth_user = headers_lower.get('x-admin-user', '')
    auth_pass = headers_lower.get('x-admin-pass', '')
    
    print(f"🔐 Auth check: user={auth_user}, pass={'*' * len(auth_pass)}")
    
    # Validate credentials
    if auth_user != 'nomade' or auth_pass != 'eternauta':
        return create_response(401, {
            'error': 'Unauthorized',
            'message': 'Invalid admin credentials'
        })
    
    try:
        # Scan DynamoDB for all spotify_user items
        response = table.scan(
            FilterExpression=Attr('user_id').begins_with('spotify_user#')
        )
        
        items = response.get('Items', [])
        
        # Format the results
        requests = []
        for item in items:
            requests.append({
                'email': item.get('email', 'Unknown'),
                'timestamp': item.get('timestamp', 'Unknown'),
                'approved': item.get('approved', False),
                'user_agent': item.get('user_agent', 'Unknown'),
                'spotify_id': item.get('spotify_id', 'Unknown')
            })
        
        # Sort by timestamp (newest first)
        requests.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        print(f"✅ Found {len(requests)} users")
        
        return create_response(200, {
            'count': len(requests),
            'requests': requests
        })
        
    except Exception as e:
        print(f"❌ Error fetching access requests: {str(e)}")
        return create_response(500, {
            'error': 'Internal server error',
            'message': str(e)
        })
