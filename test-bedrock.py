#!/usr/bin/env python3
"""Probar que Amazon Bedrock funciona"""

import json
import boto3

print("=" * 60)
print("Probando Amazon Bedrock - Claude 3 Sonnet")
print("=" * 60)

# Cliente de Bedrock
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

# Modelo a probar
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

# Payload
payload = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Di 'Hola, Bedrock funciona!' en una sola linea"
        }
    ]
}

print(f"\n[INFO] Invocando modelo: {model_id}")
print("[INFO] Esperando respuesta...\n")

try:
    # Invocar modelo
    response = bedrock.invoke_model(
        modelId=model_id,
        body=json.dumps(payload)
    )
    
    # Parsear respuesta
    response_body = json.loads(response['body'].read())
    text = response_body['content'][0]['text']
    
    print("=" * 60)
    print("[SUCCESS] Bedrock respondio!")
    print("=" * 60)
    print(f"\nRespuesta de Claude:")
    print(f"{text}\n")
    print("=" * 60)
    print("[OK] Bedrock esta funcionando correctamente!")
    print("=" * 60)
    
except Exception as e:
    print("=" * 60)
    print("[ERROR] Error al invocar Bedrock")
    print("=" * 60)
    print(f"\nError: {str(e)}\n")
    
    if "ResourceNotFoundException" in str(e):
        print("[INFO] Necesitas activar Claude en el Playground primero:")
        print("https://console.aws.amazon.com/bedrock/home?region=us-east-1#/playground")
        print("\n1. Abre el playground")
        print("2. Selecciona 'Claude 3 Sonnet'")
        print("3. Completa el formulario de caso de uso (si aparece)")
        print("4. Envia un mensaje de prueba")
        print("5. Vuelve a ejecutar este script")
    elif "AccessDeniedException" in str(e):
        print("[INFO] Tu usuario IAM necesita permisos de Bedrock")
        print("Agrega la politica: AmazonBedrockFullAccess")
    
    print("=" * 60)
