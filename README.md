# 🎵 AI DJ - Generador Inteligente de Playlists de Spotify

AI DJ es una aplicación serverless que utiliza inteligencia artificial para crear playlists personalizadas de Spotify basadas en peticiones en lenguaje natural. Interpreta el "vibe" que buscas y genera automáticamente una playlist perfecta para ti.

## 🏗️ Arquitectura

- **AWS Lambda**: Procesa las peticiones y orquesta la lógica
- **Amazon Bedrock**: Interpreta el lenguaje natural usando Claude 3 Sonnet
- **Amazon DynamoDB**: Almacena el historial de playlists por usuario
- **Amazon API Gateway**: Expone la API REST
- **Spotify Web API**: Busca canciones y crea playlists
- **AWS CDK**: Infraestructura como código en Python
- **GitHub Actions**: CI/CD automático

## 📋 Requisitos Previos

### Software Necesario (Windows)

1. **Python 3.12+**
   - Descargar desde: https://www.python.org/downloads/
   - Durante la instalación, marcar "Add Python to PATH"

2. **Node.js 20+**
   - Descargar desde: https://nodejs.org/
   - Incluye npm automáticamente

3. **AWS CLI v2**
   - Descargar desde: https://aws.amazon.com/cli/
   - Verificar instalación: `aws --version`

4. **Git**
   - Descargar desde: https://git-scm.com/download/win
   - Verificar instalación: `git --version`

5. **AWS CDK**
   ```powershell
   npm install -g aws-cdk
   cdk --version
   ```

### Cuentas Necesarias

1. **Cuenta de AWS**
   - Crear en: https://aws.amazon.com/
   - Necesitarás acceso a: Lambda, DynamoDB, API Gateway, Bedrock

2. **Cuenta de Spotify Developer**
   - Crear en: https://developer.spotify.com/dashboard
   - Crear una aplicación para obtener Client ID y Client Secret

3. **Cuenta de GitHub**
   - Para alojar el código y ejecutar CI/CD

## 🚀 Configuración del Entorno Local

### 1. Clonar o Inicializar el Repositorio

```powershell
# Si ya tienes el código
cd c:\desarrollo\workspaces\hackaton\ai-dj

# Si empiezas desde cero
git init
git remote add origin https://github.com/TU_USUARIO/ai-dj.git
```

### 2. Crear Entorno Virtual de Python

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Si tienes error de permisos, ejecuta primero:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Instalar Dependencias

```powershell
# Dependencias del proyecto CDK
pip install -r requirements.txt

# Dependencias de Lambda (para testing local)
cd lambda_src
pip install -r requirements.txt
cd ..
```

### 4. Configurar AWS CLI

```powershell
aws configure
```

Proporciona:
- **AWS Access Key ID**: Tu clave de acceso
- **AWS Secret Access Key**: Tu clave secreta
- **Default region name**: `us-east-1` (o tu región preferida)
- **Default output format**: `json`

### 5. Habilitar Amazon Bedrock

1. Ve a la consola de AWS Bedrock: https://console.aws.amazon.com/bedrock/
2. Navega a "Model access" en el menú lateral
3. Solicita acceso al modelo **Anthropic Claude 3 Sonnet**
4. Espera la aprobación (usualmente instantánea)

### 6. Configurar Spotify Developer App

1. Ve a: https://developer.spotify.com/dashboard
2. Crea una nueva aplicación
3. Anota el **Client ID** y **Client Secret**
4. En "Edit Settings", añade Redirect URIs (para autenticación de usuarios):
   - `http://localhost:8888/callback` (para desarrollo)
   - Tu URL de producción cuando la tengas

## 🔐 Configurar Secretos en GitHub

Para que el CI/CD funcione, necesitas configurar los siguientes secretos en tu repositorio de GitHub:

1. Ve a tu repositorio en GitHub
2. Navega a: **Settings** → **Secrets and variables** → **Actions**
3. Haz clic en **New repository secret** y añade:

| Nombre del Secreto | Descripción | Dónde Obtenerlo |
|-------------------|-------------|-----------------|
| `AWS_ACCESS_KEY_ID` | ID de clave de acceso de AWS | AWS IAM Console |
| `AWS_SECRET_ACCESS_KEY` | Clave de acceso secreta de AWS | AWS IAM Console |
| `AWS_ACCOUNT_ID` | ID de tu cuenta AWS (12 dígitos) | AWS Console (esquina superior derecha) |
| `SPOTIFY_CLIENT_ID` | Client ID de Spotify | Spotify Developer Dashboard |
| `SPOTIFY_CLIENT_SECRET` | Client Secret de Spotify | Spotify Developer Dashboard |

### Crear Usuario IAM para GitHub Actions

```powershell
# Crear usuario con permisos necesarios
aws iam create-user --user-name github-actions-ai-dj

# Adjuntar políticas necesarias
aws iam attach-user-policy --user-name github-actions-ai-dj --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Crear access key
aws iam create-access-key --user-name github-actions-ai-dj
```

**Nota**: En producción, usa permisos más restrictivos en lugar de `AdministratorAccess`.

## 🧪 Despliegue Local (Opcional)

Para probar el despliegue desde tu máquina local:

```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Configurar variables de entorno
$env:SPOTIFY_CLIENT_ID = "tu_client_id"
$env:SPOTIFY_CLIENT_SECRET = "tu_client_secret"

# Bootstrap de CDK (solo primera vez)
cdk bootstrap

# Sintetizar el stack (verificar que no hay errores)
cdk synth

# Desplegar
cdk deploy

# Ver los outputs (API endpoint, etc.)
cdk deploy --outputs-file outputs.json
```

## 🚢 Despliegue Automático con GitHub Actions

### Primera Vez

1. **Asegúrate de tener todos los secretos configurados** (ver sección anterior)

2. **Haz commit de tu código**:
   ```powershell
   git add .
   git commit -m "Initial commit: AI DJ serverless app"
   ```

3. **Sube a la rama main**:
   ```powershell
   git push origin main
   ```

4. **Monitorea el despliegue**:
   - Ve a tu repositorio en GitHub
   - Navega a la pestaña **Actions**
   - Verás el workflow "Deploy AI DJ to AWS" ejecutándose
   - Haz clic en el workflow para ver los logs en tiempo real

### Despliegues Posteriores

Cada vez que hagas `git push` a la rama `main`, se desplegará automáticamente:

```powershell
# Hacer cambios en el código
# ...

# Commit y push
git add .
git commit -m "Descripción de tus cambios"
git push origin main
```

## 📡 Uso de la API

Una vez desplegada, obtendrás un endpoint de API Gateway. Ejemplo:

```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/
```

### Endpoint: POST /playlist

**Request**:
```json
{
  "user_id": "usuario123",
  "prompt": "Música energética para hacer ejercicio, algo de rock y electrónica",
  "spotify_access_token": "BQD...token_del_usuario"
}
```

**Response**:
```json
{
  "message": "Playlist created successfully",
  "playlist_url": "https://open.spotify.com/playlist/abc123",
  "tracks_count": 20,
  "parameters": {
    "genres": ["rock", "electronic"],
    "mood": "energetic",
    "energy": 0.8,
    "danceability": 0.7,
    "valence": 0.6,
    "playlist_name": "AI DJ - Workout Mix"
  }
}
```

### Obtener Access Token de Spotify

Los usuarios deben autenticarse con Spotify usando OAuth 2.0. Ejemplo básico:

1. **Authorization Code Flow**: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
2. **Scopes necesarios**: `playlist-modify-public`, `playlist-modify-private`

## 🧹 Limpieza de Recursos

Para eliminar todos los recursos de AWS y evitar cargos:

```powershell
# Desde tu máquina local
cdk destroy

# Confirma con 'y' cuando se te pregunte
```

O desde GitHub Actions, puedes crear un workflow manual de destrucción.

## 📊 Monitoreo y Logs

### Ver logs de Lambda

```powershell
# Usando AWS CLI
aws logs tail /aws/lambda/AI-DJ-Handler --follow

# O desde la consola de AWS
# CloudWatch → Log groups → /aws/lambda/AI-DJ-Handler
```

### Ver métricas

- **Lambda**: CloudWatch → Metrics → Lambda → By Function Name
- **API Gateway**: CloudWatch → Metrics → ApiGateway
- **DynamoDB**: CloudWatch → Metrics → DynamoDB → Table Metrics

## 🔧 Troubleshooting

### Error: "Unable to locate credentials"

```powershell
# Verificar configuración de AWS
aws configure list

# Reconfigurar si es necesario
aws configure
```

### Error: "Access Denied" en Bedrock

- Verifica que has solicitado acceso al modelo Claude 3 Sonnet en la consola de Bedrock
- Asegúrate de estar en la región correcta (us-east-1)

### Error: "Invalid client" en Spotify

- Verifica que `SPOTIFY_CLIENT_ID` y `SPOTIFY_CLIENT_SECRET` sean correctos
- Asegúrate de que las variables de entorno estén configuradas en GitHub Secrets

### Pipeline de GitHub Actions falla

- Verifica que todos los secretos estén configurados correctamente
- Revisa los logs del workflow en la pestaña Actions
- Asegúrate de que el usuario IAM tenga los permisos necesarios

## 📝 Estructura del Proyecto

```
ai-dj/
├── .github/
│   └── workflows/
│       └── deploy.yml          # Pipeline CI/CD
├── ai_dj/
│   ├── __init__.py
│   └── ai_dj_stack.py         # Definición de infraestructura CDK
├── lambda_src/
│   ├── __init__.py
│   ├── app.py                 # Código de la Lambda
│   └── requirements.txt       # Dependencias de Lambda
├── app.py                     # Punto de entrada de CDK
├── cdk.json                   # Configuración de CDK
├── requirements.txt           # Dependencias del proyecto CDK
├── .gitignore
└── README.md
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🎯 Próximos Pasos

- [ ] Implementar autenticación de usuarios con Cognito
- [ ] Añadir frontend web con React
- [ ] Soporte para múltiples modelos de IA
- [ ] Análisis de sentimiento más avanzado
- [ ] Integración con otras plataformas de música
- [ ] Tests unitarios y de integración
- [ ] Documentación de API con OpenAPI/Swagger

## 📞 Soporte

Si tienes problemas o preguntas:
- Abre un issue en GitHub
- Revisa la documentación de AWS CDK: https://docs.aws.amazon.com/cdk/
- Consulta la API de Spotify: https://developer.spotify.com/documentation/web-api
- Documentación de Bedrock: https://docs.aws.amazon.com/bedrock/

---

**¡Disfruta creando playlists con IA! 🎵🤖**
