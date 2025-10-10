#!/usr/bin/env python3
import os
import aws_cdk as cdk
from ai_dj.ai_dj_stack import AiDjStack

app = cdk.App()

# Obtener variables de entorno para Spotify
spotify_client_id = os.environ.get('SPOTIFY_CLIENT_ID', '')
spotify_client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET', '')

AiDjStack(
    app, 
    "AiDjStack",
    spotify_client_id=spotify_client_id,
    spotify_client_secret=spotify_client_secret,
    env=cdk.Environment(
        account=os.environ.get('CDK_DEFAULT_ACCOUNT'),
        region=os.environ.get('CDK_DEFAULT_REGION', 'us-east-1')
    ),
    description="AI DJ - Serverless Spotify Playlist Generator"
)

app.synth()
