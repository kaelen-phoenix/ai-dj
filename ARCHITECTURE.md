# 🏗️ Arquitectura de AI DJ

## Diagrama de Arquitectura

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │ HTTP POST /playlist
       │ {user_id, prompt, spotify_access_token}
       ▼
┌─────────────────────────────────────────┐
│     Amazon API Gateway (HTTP API)       │
│  - CORS habilitado                      │
│  - Ruta: POST /playlist                 │
└──────────────┬──────────────────────────┘
               │ Invoca
               ▼
┌─────────────────────────────────────────┐
│         AWS Lambda Function             │
│  - Runtime: Python 3.12                 │
│  - Timeout: 60s                         │
│  - Memory: 512 MB                       │
│  - Handler: app.lambda_handler          │
└──┬────────┬────────┬────────────────────┘
   │        │        │
   │        │        └──────────────────┐
   │        │                           │
   │        │ Invoca modelo             │ Lee/Escribe
   │        ▼                           ▼
   │  ┌──────────────────┐    ┌──────────────────┐
   │  │ Amazon Bedrock   │    │ Amazon DynamoDB  │
   │  │ Claude 3 Sonnet  │    │ Tabla: AI-DJ-    │
   │  │                  │    │ Users            │
   │  │ Interpreta       │    │ PK: user_id      │
   │  │ lenguaje natural │    │                  │
   │  │ → parámetros     │    │ Almacena:        │
   │  │   musicales      │    │ - Historial      │
   │  └──────────────────┘    │ - Playlists      │
   │                          └──────────────────┘
   │
   │ Busca canciones y crea playlist
   ▼
┌─────────────────────────────────────────┐
│         Spotify Web API                 │
│  - Search tracks                        │
│  - Get audio features                   │
│  - Create playlist                      │
│  - Add tracks to playlist               │
└─────────────────────────────────────────┘
```

## Flujo de Datos Detallado

### 1. Recepción de Petición

```
Usuario → API Gateway → Lambda
```

**Payload de entrada**:
```json
{
  "user_id": "usuario123",
  "prompt": "Música energética para hacer ejercicio",
  "spotify_access_token": "BQD...token"
}
```

### 2. Interpretación con IA

```
Lambda → Bedrock (Claude 3 Sonnet)
```

**Prompt al modelo**:
```
Sistema: Eres un experto en música que interpreta peticiones...
Usuario: Crea una playlist basada en: Música energética para hacer ejercicio
```

**Respuesta del modelo**:
```json
{
  "genres": ["rock", "electronic", "pop"],
  "mood": "energetic",
  "energy": 0.85,
  "danceability": 0.75,
  "valence": 0.7,
  "tempo": 140,
  "popularity": 60,
  "playlist_name": "AI DJ - Workout Energy",
  "limit": 20
}
```

### 3. Búsqueda de Canciones

```
Lambda → Spotify API (Search)
```

**Request**:
```
GET /v1/search?q=genre:"rock" OR genre:"electronic"&type=track&limit=50
Authorization: Bearer {spotify_access_token}
```

**Response**: Lista de 50 canciones candidatas

### 4. Filtrado por Audio Features

```
Lambda → Spotify API (Audio Features)
```

**Request**:
```
GET /v1/audio-features?ids=track1,track2,...,track50
Authorization: Bearer {spotify_access_token}
```

**Response**: Características de audio de cada canción

**Algoritmo de filtrado**:
```python
for track, features in zip(tracks, audio_features):
    energy_diff = abs(features['energy'] - target_energy)
    dance_diff = abs(features['danceability'] - target_danceability)
    valence_diff = abs(features['valence'] - target_valence)
    
    score = 1 - (energy_diff + dance_diff + valence_diff) / 3
    
    if track['popularity'] >= min_popularity:
        filtered_tracks.append({'track': track, 'score': score})

# Ordenar por score y tomar los mejores
filtered_tracks.sort(key=lambda x: x['score'], reverse=True)
best_tracks = filtered_tracks[:limit]
```

### 5. Creación de Playlist

```
Lambda → Spotify API (Create Playlist)
```

**Request 1**: Obtener Spotify User ID
```
GET /v1/me
Authorization: Bearer {spotify_access_token}
```

**Request 2**: Crear playlist
```
POST /v1/users/{user_id}/playlists
{
  "name": "AI DJ - Workout Energy",
  "description": "Created by AI DJ - 2025-10-10 03:48 UTC",
  "public": true
}
```

**Request 3**: Añadir canciones
```
POST /v1/playlists/{playlist_id}/tracks
{
  "uris": ["spotify:track:abc123", "spotify:track:def456", ...]
}
```

### 6. Almacenamiento en DynamoDB

```
Lambda → DynamoDB
```

**Operación**: PutItem

**Item**:
```json
{
  "user_id": "usuario123",
  "playlists": [
    {
      "playlist_url": "https://open.spotify.com/playlist/xyz789",
      "prompt": "Música energética para hacer ejercicio",
      "parameters": {
        "genres": ["rock", "electronic"],
        "mood": "energetic",
        "energy": 0.85
      },
      "created_at": "2025-10-10T03:48:00.000Z"
    }
  ],
  "last_updated": "2025-10-10T03:48:00.000Z"
}
```

### 7. Respuesta al Usuario

```
Lambda → API Gateway → Usuario
```

**Response**:
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": {
    "message": "Playlist created successfully",
    "playlist_url": "https://open.spotify.com/playlist/xyz789",
    "tracks_count": 20,
    "parameters": {
      "genres": ["rock", "electronic"],
      "mood": "energetic",
      "energy": 0.85,
      "danceability": 0.75,
      "valence": 0.7
    }
  }
}
```

## Componentes de AWS

### AWS Lambda

**Configuración**:
- **Runtime**: Python 3.12
- **Handler**: `app.lambda_handler`
- **Timeout**: 60 segundos
- **Memory**: 512 MB
- **Concurrency**: Sin límite (por defecto)

**Variables de entorno**:
- `SPOTIFY_CLIENT_ID`: ID de cliente de Spotify
- `SPOTIFY_CLIENT_SECRET`: Secret de cliente de Spotify
- `DYNAMODB_TABLE_NAME`: Nombre de la tabla DynamoDB
- `BEDROCK_MODEL_ID`: ID del modelo de Bedrock
- `AWS_REGION`: Región de AWS (automática)

**Permisos IAM**:
- `dynamodb:GetItem`
- `dynamodb:PutItem`
- `bedrock:InvokeModel`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

### Amazon API Gateway

**Tipo**: HTTP API (más económico y simple que REST API)

**Configuración**:
- **CORS**: Habilitado para todos los orígenes
- **Métodos permitidos**: POST, OPTIONS
- **Headers permitidos**: Content-Type, Authorization

**Rutas**:
- `POST /playlist` → Lambda Integration

**Throttling**: Sin límites personalizados (usa defaults de AWS)

### Amazon DynamoDB

**Configuración**:
- **Nombre**: AI-DJ-Users
- **Partition Key**: `user_id` (String)
- **Billing Mode**: Pay-per-request (on-demand)
- **Point-in-time recovery**: Habilitado

**Estructura de datos**:
```
{
  "user_id": "String (PK)",
  "playlists": [
    {
      "playlist_url": "String",
      "prompt": "String",
      "parameters": {
        "genres": ["String"],
        "mood": "String",
        "energy": Number,
        ...
      },
      "created_at": "String (ISO 8601)"
    }
  ],
  "last_updated": "String (ISO 8601)"
}
```

**Patrones de acceso**:
1. Obtener historial de un usuario: `GetItem(user_id)`
2. Guardar nueva playlist: `PutItem(user_id, playlists)`

### Amazon Bedrock

**Modelo**: `anthropic.claude-3-sonnet-20240229-v1:0`

**Características**:
- **Contexto**: 200K tokens
- **Salida máxima**: 4K tokens
- **Multimodal**: Sí (texto e imágenes)
- **Velocidad**: ~50 tokens/segundo

**Uso en AI DJ**:
- Interpretación de lenguaje natural
- Extracción de parámetros musicales
- Generación de nombres de playlists

**Costo estimado**:
- Input: $0.003 / 1K tokens
- Output: $0.015 / 1K tokens
- ~$0.02 por petición

## Infraestructura como Código (CDK)

### Stack Principal: `AiDjStack`

**Recursos creados**:
1. DynamoDB Table
2. Lambda Function
3. IAM Role (para Lambda)
4. IAM Policies (permisos)
5. API Gateway HTTP API
6. Lambda Integration
7. CloudWatch Log Groups (automático)

**Outputs**:
- `ApiEndpoint`: URL del API Gateway
- `DynamoDBTableName`: Nombre de la tabla
- `LambdaFunctionName`: Nombre de la función

### Dependencias

**CDK (requirements.txt)**:
```
aws-cdk-lib==2.149.0
constructs>=10.0.0,<11.0.0
```

**Lambda (lambda_src/requirements.txt)**:
```
boto3>=1.34.0
requests>=2.31.0
```

## CI/CD con GitHub Actions

### Workflow: `deploy.yml`

**Triggers**:
- Push a rama `main`
- Manual (workflow_dispatch)

**Jobs**:
1. **Checkout**: Clonar código
2. **Configure AWS**: Autenticación con AWS
3. **Setup Node.js**: Instalar Node.js 20
4. **Install CDK**: Instalar AWS CDK CLI
5. **Setup Python**: Instalar Python 3.12
6. **Install Dependencies**: Instalar dependencias CDK y Lambda
7. **CDK Synth**: Sintetizar CloudFormation
8. **CDK Bootstrap**: Preparar entorno (solo primera vez)
9. **CDK Deploy**: Desplegar stack
10. **Display Outputs**: Mostrar resultados
11. **Upload Artifacts**: Guardar outputs.json

**Secretos requeridos**:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_ACCOUNT_ID`
- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`

## Seguridad

### Autenticación y Autorización

**API Gateway**:
- Sin autenticación (público)
- CORS configurado
- Rate limiting por defecto de AWS

**Spotify**:
- OAuth 2.0
- Access token del usuario requerido
- Scopes: `playlist-modify-public`, `playlist-modify-private`

**AWS**:
- IAM roles con permisos mínimos
- Credenciales en GitHub Secrets
- No hay credenciales hardcodeadas

### Datos Sensibles

**Variables de entorno**:
- Encriptadas en Lambda
- Inyectadas en tiempo de despliegue
- No expuestas en logs

**DynamoDB**:
- Encriptación en reposo (por defecto)
- Encriptación en tránsito (HTTPS)
- Backups automáticos con PITR

### Mejores Prácticas Implementadas

1. ✅ Principio de menor privilegio (IAM)
2. ✅ Secretos en variables de entorno
3. ✅ HTTPS en todas las comunicaciones
4. ✅ Validación de inputs
5. ✅ Manejo de errores
6. ✅ Logging estructurado
7. ✅ Encriptación de datos

## Escalabilidad

### Límites y Capacidad

**Lambda**:
- **Concurrencia**: 1000 ejecuciones simultáneas (por defecto)
- **Escalado**: Automático
- **Cold start**: ~1-2 segundos

**API Gateway**:
- **Requests**: 10,000 RPS (por defecto)
- **Throttling**: Configurable

**DynamoDB**:
- **Capacidad**: Ilimitada (on-demand)
- **Throughput**: Automático
- **Latencia**: <10ms (p99)

**Bedrock**:
- **Throttling**: 200 requests/minuto (por defecto)
- **Tokens**: 200K input, 4K output

### Optimizaciones Potenciales

1. **Lambda**:
   - Provisioned concurrency para eliminar cold starts
   - Aumentar memoria para más CPU
   - Reutilizar conexiones HTTP

2. **DynamoDB**:
   - DAX (cache) para lecturas frecuentes
   - Global tables para multi-región
   - Índices secundarios para queries complejas

3. **API Gateway**:
   - Cache de respuestas
   - API Keys para rate limiting por usuario
   - WAF para protección DDoS

4. **Bedrock**:
   - Cache de respuestas comunes
   - Batch processing
   - Modelo más pequeño (Haiku) para casos simples

## Costos Estimados

### Por Petición

- **Lambda**: $0.0000002 (200ms @ 512MB)
- **API Gateway**: $0.000001
- **DynamoDB**: $0.00000125 (1 write + 1 read)
- **Bedrock**: $0.02 (promedio)
- **Spotify API**: Gratis
- **Total**: ~$0.021 por playlist creada

### Mensual (1000 playlists)

- **Lambda**: $0.20
- **API Gateway**: $1.00
- **DynamoDB**: $1.25
- **Bedrock**: $20.00
- **Total**: ~$22.45/mes

### Free Tier (primer año)

- **Lambda**: 1M requests/mes gratis
- **API Gateway**: 1M requests/mes gratis
- **DynamoDB**: 25GB storage + 25 WCU/RCU gratis
- **Bedrock**: No tiene free tier

## Monitoreo y Observabilidad

### CloudWatch Metrics

**Lambda**:
- Invocations
- Duration
- Errors
- Throttles
- Concurrent executions

**API Gateway**:
- Count (requests)
- 4XXError
- 5XXError
- Latency
- IntegrationLatency

**DynamoDB**:
- ConsumedReadCapacityUnits
- ConsumedWriteCapacityUnits
- UserErrors
- SystemErrors

### CloudWatch Logs

**Lambda logs**:
```
/aws/lambda/AI-DJ-Handler
```

**Logs estructurados**:
```python
print(f"Processing request for user_id: {user_id}")
print(f"Extracted music parameters: {music_parameters}")
print(f"Found {len(tracks)} tracks")
print(f"Created playlist: {playlist_url}")
```

### Alarmas Recomendadas

1. **Lambda Errors > 5% en 5 minutos**
2. **API Gateway 5XX > 1% en 5 minutos**
3. **Lambda Duration > 50 segundos**
4. **DynamoDB Throttled Requests > 0**

## Testing

### Pruebas Locales

**Lambda**:
```python
# test_lambda.py
from lambda_src.app import lambda_handler

event = {
    'body': json.dumps({
        'user_id': 'test',
        'prompt': 'happy music',
        'spotify_access_token': 'token'
    })
}

response = lambda_handler(event, None)
print(response)
```

**CDK**:
```powershell
cdk synth
cdk diff
```

### Pruebas de Integración

```powershell
# Desplegar a entorno de test
cdk deploy --context env=test

# Ejecutar pruebas
pytest tests/integration/

# Limpiar
cdk destroy --context env=test
```

## Roadmap de Mejoras

### Corto Plazo
- [ ] Autenticación de usuarios (Cognito)
- [ ] Rate limiting por usuario
- [ ] Cache de resultados de Bedrock
- [ ] Tests unitarios

### Medio Plazo
- [ ] Frontend web (React)
- [ ] Múltiples modelos de IA
- [ ] Análisis de sentimiento avanzado
- [ ] Métricas de uso

### Largo Plazo
- [ ] Multi-región
- [ ] Integración con otras plataformas (Apple Music, YouTube Music)
- [ ] Recomendaciones personalizadas
- [ ] API pública con documentación OpenAPI

---

**Última actualización**: 2025-10-10
