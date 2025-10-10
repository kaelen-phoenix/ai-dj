# 📡 API Documentation - AI DJ

## Base URL

```
https://{api-id}.execute-api.{region}.amazonaws.com/
```

Ejemplo:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/
```

## Authentication

La API no requiere autenticación a nivel de API Gateway, pero **sí requiere un Spotify Access Token válido** en el body de la petición.

### Obtener Spotify Access Token

Debes implementar el flujo OAuth 2.0 de Spotify. Ver: [Spotify Authorization Guide](https://developer.spotify.com/documentation/web-api/tutorials/code-flow)

**Scopes requeridos**:
- `playlist-modify-public`
- `playlist-modify-private`
- `user-read-private`
- `user-read-email`

## Endpoints

### POST /playlist

Crea una nueva playlist de Spotify basada en un prompt en lenguaje natural.

#### Request

**Headers**:
```
Content-Type: application/json
```

**Body**:
```json
{
  "user_id": "string (required)",
  "prompt": "string (required)",
  "spotify_access_token": "string (required)"
}
```

**Parámetros**:

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `user_id` | string | Sí | Identificador único del usuario |
| `prompt` | string | Sí | Descripción en lenguaje natural de la playlist deseada |
| `spotify_access_token` | string | Sí | Token de acceso de Spotify OAuth 2.0 |

**Ejemplo**:
```json
{
  "user_id": "usuario123",
  "prompt": "Música energética para hacer ejercicio, algo de rock y electrónica",
  "spotify_access_token": "BQDxO8F...token_completo"
}
```

#### Response

**Success (200 OK)**:
```json
{
  "message": "Playlist created successfully",
  "playlist_url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M",
  "tracks_count": 20,
  "parameters": {
    "genres": ["rock", "electronic"],
    "mood": "energetic",
    "energy": 0.85,
    "danceability": 0.75,
    "valence": 0.7,
    "tempo": 140,
    "popularity": 60,
    "playlist_name": "AI DJ - Workout Energy",
    "limit": 20
  }
}
```

**Error (400 Bad Request)**:
```json
{
  "error": "Missing required parameters: user_id and prompt are required"
}
```

**Error (404 Not Found)**:
```json
{
  "error": "No tracks found matching the criteria"
}
```

**Error (500 Internal Server Error)**:
```json
{
  "error": "Internal server error: {error_message}"
}
```

#### Response Fields

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `message` | string | Mensaje de éxito |
| `playlist_url` | string | URL pública de la playlist en Spotify |
| `tracks_count` | integer | Número de canciones añadidas a la playlist |
| `parameters` | object | Parámetros musicales extraídos del prompt |
| `parameters.genres` | array[string] | Géneros musicales identificados |
| `parameters.mood` | string | Estado de ánimo de la playlist |
| `parameters.energy` | float | Nivel de energía (0.0 - 1.0) |
| `parameters.danceability` | float | Qué tan bailable (0.0 - 1.0) |
| `parameters.valence` | float | Positividad (0.0 - 1.0) |
| `parameters.tempo` | integer | Tempo en BPM (opcional) |
| `parameters.popularity` | integer | Popularidad mínima (0 - 100) |
| `parameters.playlist_name` | string | Nombre generado para la playlist |
| `parameters.limit` | integer | Número de canciones solicitadas |

## Examples

### cURL

```bash
curl -X POST https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "usuario123",
    "prompt": "Música relajante para estudiar, jazz y lo-fi",
    "spotify_access_token": "BQDxO8F...token"
  }'
```

### PowerShell

```powershell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    user_id = "usuario123"
    prompt = "Música relajante para estudiar, jazz y lo-fi"
    spotify_access_token = "BQDxO8F...token"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist" `
    -Method Post `
    -Headers $headers `
    -Body $body
```

### Python

```python
import requests

url = "https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist"

payload = {
    "user_id": "usuario123",
    "prompt": "Música relajante para estudiar, jazz y lo-fi",
    "spotify_access_token": "BQDxO8F...token"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const url = 'https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist';

const payload = {
  user_id: 'usuario123',
  prompt: 'Música relajante para estudiar, jazz y lo-fi',
  spotify_access_token: 'BQDxO8F...token'
};

axios.post(url, payload)
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.error(error.response.data);
  });
```

### JavaScript (Fetch API)

```javascript
const url = 'https://abc123xyz.execute-api.us-east-1.amazonaws.com/playlist';

const payload = {
  user_id: 'usuario123',
  prompt: 'Música relajante para estudiar, jazz y lo-fi',
  spotify_access_token: 'BQDxO8F...token'
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
```

## Prompt Examples

Aquí hay ejemplos de prompts que funcionan bien:

### Por Actividad

```json
{
  "prompt": "Música para correr, ritmo rápido y energético"
}
```

```json
{
  "prompt": "Playlist para trabajar concentrado, música instrumental sin letra"
}
```

```json
{
  "prompt": "Música para una fiesta, reggaeton y música latina bailable"
}
```

### Por Género

```json
{
  "prompt": "Rock clásico de los 70s y 80s, bandas icónicas"
}
```

```json
{
  "prompt": "Jazz suave para una cena romántica"
}
```

```json
{
  "prompt": "Música electrónica para bailar, house y techno"
}
```

### Por Estado de Ánimo

```json
{
  "prompt": "Música triste para llorar, baladas emotivas"
}
```

```json
{
  "prompt": "Canciones alegres y optimistas para empezar el día"
}
```

```json
{
  "prompt": "Música relajante para meditar y hacer yoga"
}
```

### Combinaciones Complejas

```json
{
  "prompt": "Indie rock alternativo de los 2000s, bandas poco conocidas, ritmo medio"
}
```

```json
{
  "prompt": "Música latina moderna, mezcla de reggaeton, salsa y bachata, para bailar"
}
```

```json
{
  "prompt": "Clásicos del hip hop de los 90s, rap de la costa este, beats old school"
}
```

## Rate Limits

### API Gateway Defaults

- **Burst**: 5,000 requests
- **Steady-state**: 10,000 requests/segundo

### Bedrock Limits

- **Requests**: 200 requests/minuto
- **Tokens**: 200K input tokens/minuto

### Spotify API Limits

- **Rate limit**: Variable según endpoint
- **Retry-After**: Header incluido en respuestas 429

## Error Handling

### Error Codes

| Status Code | Descripción |
|-------------|-------------|
| 200 | Success - Playlist creada correctamente |
| 400 | Bad Request - Parámetros faltantes o inválidos |
| 401 | Unauthorized - Token de Spotify inválido o expirado |
| 404 | Not Found - No se encontraron canciones |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Error en el servidor |
| 503 | Service Unavailable - Servicio temporalmente no disponible |

### Error Response Format

```json
{
  "error": "Descripción del error"
}
```

### Common Errors

#### Invalid Spotify Token

```json
{
  "error": "Internal server error: The access token expired"
}
```

**Solución**: Renovar el access token usando el refresh token de OAuth 2.0.

#### Missing Parameters

```json
{
  "error": "Missing required parameters: user_id and prompt are required"
}
```

**Solución**: Asegurarse de incluir `user_id`, `prompt` y `spotify_access_token`.

#### No Tracks Found

```json
{
  "error": "No tracks found matching the criteria"
}
```

**Solución**: Intentar con un prompt diferente o más general.

## CORS

La API tiene CORS habilitado con la siguiente configuración:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

Esto permite llamadas desde cualquier dominio (frontend web).

## Best Practices

### 1. Token Management

- Almacena el access token de forma segura
- Implementa refresh automático cuando expire
- No expongas el token en URLs o logs

### 2. Error Handling

```javascript
try {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error);
  }
  
  const data = await response.json();
  return data;
} catch (error) {
  console.error('Error creating playlist:', error.message);
  // Manejar error apropiadamente
}
```

### 3. Retry Logic

```python
import time
import requests

def create_playlist_with_retry(payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit - esperar y reintentar
                retry_after = int(e.response.headers.get('Retry-After', 5))
                time.sleep(retry_after)
            elif attempt == max_retries - 1:
                raise
            else:
                time.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Prompt Optimization

**Buenos prompts**:
- ✅ Específicos: "Rock alternativo de los 90s"
- ✅ Descriptivos: "Música energética para correr"
- ✅ Con contexto: "Jazz suave para una cena romántica"

**Prompts a evitar**:
- ❌ Muy vagos: "música"
- ❌ Contradictorios: "música relajante y energética"
- ❌ Demasiado específicos: "solo canciones de exactamente 3:45 minutos"

## Monitoring

### CloudWatch Metrics

Puedes monitorear el uso de la API en CloudWatch:

```powershell
# Ver métricas de API Gateway
aws cloudwatch get-metric-statistics `
  --namespace AWS/ApiGateway `
  --metric-name Count `
  --dimensions Name=ApiId,Value=abc123xyz `
  --start-time 2025-10-10T00:00:00Z `
  --end-time 2025-10-10T23:59:59Z `
  --period 3600 `
  --statistics Sum
```

### CloudWatch Logs

```powershell
# Ver logs de Lambda
aws logs tail /aws/lambda/AI-DJ-Handler --follow
```

## Changelog

### Version 1.0.0 (2025-10-10)

- ✨ Initial release
- 🎵 POST /playlist endpoint
- 🤖 Integration with Amazon Bedrock (Claude 3 Sonnet)
- 🎧 Spotify playlist creation
- 💾 DynamoDB storage for user history

## Support

Para reportar problemas o solicitar features:
- GitHub Issues: [tu-repo]/issues
- Email: support@ai-dj.com (ejemplo)

## License

MIT License - Ver LICENSE file para detalles.

---

**API Version**: 1.0.0  
**Last Updated**: 2025-10-10  
**Region**: us-east-1
