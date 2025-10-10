# ⚡ Quick Start - AI DJ

Guía rápida para desarrolladores experimentados que quieren desplegar AI DJ en menos de 15 minutos.

## Prerrequisitos

- ✅ Python 3.12+
- ✅ Node.js 20+
- ✅ AWS CLI configurado
- ✅ Cuenta AWS con acceso a Bedrock
- ✅ Spotify Developer App (Client ID + Secret)
- ✅ GitHub account

## Instalación Rápida (Windows)

### 1. Instalar Herramientas

```powershell
# Python
winget install Python.Python.3.12

# Node.js
winget install OpenJS.NodeJS

# AWS CLI
winget install Amazon.AWSCLI

# Git
winget install Git.Git

# AWS CDK
npm install -g aws-cdk
```

### 2. Configurar AWS

```powershell
# Configurar credenciales
aws configure
# AWS Access Key ID: [tu_key]
# AWS Secret Access Key: [tu_secret]
# Default region: us-east-1
# Default output: json

# Habilitar Bedrock Claude 3 Sonnet
# Ve a: https://console.aws.amazon.com/bedrock/
# Model access → Request access → Anthropic Claude 3 Sonnet
```

### 3. Clonar y Configurar Proyecto

```powershell
# Clonar
cd c:\desarrollo\workspaces\hackaton
git clone https://github.com/TU_USUARIO/ai-dj.git
cd ai-dj

# Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
cd lambda_src
pip install -r requirements.txt
cd ..
```

### 4. Desplegar

```powershell
# Configurar variables de entorno
$env:SPOTIFY_CLIENT_ID = "tu_spotify_client_id"
$env:SPOTIFY_CLIENT_SECRET = "tu_spotify_client_secret"

# Bootstrap CDK (solo primera vez)
cdk bootstrap

# Desplegar
cdk deploy

# Copiar el API Endpoint del output
```

### 5. Configurar GitHub Actions

1. Sube el código a GitHub:
   ```powershell
   git remote add origin https://github.com/TU_USUARIO/ai-dj.git
   git branch -M main
   git push -u origin main
   ```

2. Configura secretos en GitHub (Settings → Secrets → Actions):
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_ACCOUNT_ID`
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`

3. Próximo push desplegará automáticamente:
   ```powershell
   git add .
   git commit -m "Update"
   git push
   ```

## Probar la API

```powershell
# Guardar endpoint
$API = "https://tu-endpoint.execute-api.us-east-1.amazonaws.com"

# Llamar API (necesitas un Spotify access token válido)
$body = @{
    user_id = "test_user"
    prompt = "Música energética para hacer ejercicio"
    spotify_access_token = "TU_SPOTIFY_TOKEN"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$API/playlist" -Method Post -Body $body -ContentType "application/json"
```

## Estructura del Proyecto

```
ai-dj/
├── .github/workflows/deploy.yml    # CI/CD
├── ai_dj/
│   └── ai_dj_stack.py             # Infraestructura CDK
├── lambda_src/
│   ├── app.py                     # Lambda handler
│   └── requirements.txt           # Dependencias Lambda
├── app.py                         # Entry point CDK
├── cdk.json                       # Config CDK
└── requirements.txt               # Dependencias CDK
```

## Comandos Útiles

```powershell
# Sintetizar CloudFormation
cdk synth

# Ver diferencias antes de desplegar
cdk diff

# Desplegar
cdk deploy

# Ver logs de Lambda
aws logs tail /aws/lambda/AI-DJ-Handler --follow

# Destruir stack
cdk destroy
```

## Recursos AWS Creados

- **Lambda Function**: `AI-DJ-Handler`
- **DynamoDB Table**: `AI-DJ-Users`
- **API Gateway**: `AI-DJ-API`
- **IAM Role**: Para Lambda con permisos DynamoDB y Bedrock
- **CloudWatch Log Group**: `/aws/lambda/AI-DJ-Handler`

## Costos Estimados

- **Lambda**: ~$0.20/mes (1000 invocaciones)
- **API Gateway**: ~$1.00/mes (1000 requests)
- **DynamoDB**: ~$1.25/mes (on-demand)
- **Bedrock**: ~$20.00/mes (1000 requests)
- **Total**: ~$22.45/mes

## Troubleshooting

### Error: "Unable to locate credentials"
```powershell
aws configure
```

### Error: "Access Denied" en Bedrock
- Habilita Claude 3 Sonnet en la consola de Bedrock (us-east-1)

### Error: "Invalid client" en Spotify
- Verifica Client ID y Secret en Spotify Developer Dashboard

### GitHub Actions falla
- Verifica que todos los secretos estén configurados
- Revisa los logs en la pestaña Actions

## Próximos Pasos

1. **Implementar autenticación Spotify**: Ver `SPOTIFY_AUTH_GUIDE.md`
2. **Crear frontend**: React + TailwindCSS
3. **Añadir tests**: pytest + moto
4. **Configurar alarmas**: CloudWatch Alarms

## Documentación Completa

- **Setup detallado**: `SETUP_GUIDE.md`
- **Arquitectura**: `ARCHITECTURE.md`
- **API Reference**: `API_DOCUMENTATION.md`
- **Spotify OAuth**: `SPOTIFY_AUTH_GUIDE.md`

## Soporte

- GitHub Issues: https://github.com/TU_USUARIO/ai-dj/issues
- AWS CDK Docs: https://docs.aws.amazon.com/cdk/
- Spotify API: https://developer.spotify.com/documentation/

---

**¡Listo para crear playlists con IA! 🎵🤖**
