# 📘 Guía de Configuración Completa - AI DJ en Windows

Esta guía te llevará paso a paso desde cero hasta tener tu aplicación AI DJ desplegada automáticamente en AWS.

## 📑 Índice

1. [Instalación de Software Base](#1-instalación-de-software-base)
2. [Configuración de AWS](#2-configuración-de-aws)
3. [Configuración de Spotify](#3-configuración-de-spotify)
4. [Configuración del Proyecto Local](#4-configuración-del-proyecto-local)
5. [Configuración de GitHub](#5-configuración-de-github)
6. [Primer Despliegue](#6-primer-despliegue)
7. [Verificación](#7-verificación)

---

## 1. Instalación de Software Base

### 1.1 Python 3.12

1. Descarga Python desde: https://www.python.org/downloads/
2. Ejecuta el instalador
3. **IMPORTANTE**: Marca la casilla "Add Python to PATH"
4. Haz clic en "Install Now"
5. Verifica la instalación:
   ```powershell
   python --version
   # Debe mostrar: Python 3.12.x
   ```

### 1.2 Node.js 20

1. Descarga Node.js desde: https://nodejs.org/
2. Ejecuta el instalador (usa las opciones por defecto)
3. Verifica la instalación:
   ```powershell
   node --version
   # Debe mostrar: v20.x.x
   
   npm --version
   # Debe mostrar: 10.x.x
   ```

### 1.3 AWS CLI

1. Descarga AWS CLI v2 desde: https://awscli.amazonaws.com/AWSCLIV2.msi
2. Ejecuta el instalador
3. Verifica la instalación:
   ```powershell
   aws --version
   # Debe mostrar: aws-cli/2.x.x
   ```

### 1.4 Git

1. Descarga Git desde: https://git-scm.com/download/win
2. Ejecuta el instalador (usa las opciones por defecto)
3. Verifica la instalación:
   ```powershell
   git --version
   # Debe mostrar: git version 2.x.x
   ```

### 1.5 AWS CDK

```powershell
# Instalar globalmente
npm install -g aws-cdk

# Verificar instalación
cdk --version
# Debe mostrar: 2.x.x
```

---

## 2. Configuración de AWS

### 2.1 Crear Cuenta de AWS

1. Ve a: https://aws.amazon.com/
2. Haz clic en "Create an AWS Account"
3. Completa el proceso de registro (necesitarás una tarjeta de crédito)
4. Anota tu **Account ID** (12 dígitos) - lo encontrarás en la esquina superior derecha

### 2.2 Crear Usuario IAM para Desarrollo

1. Ve a la consola de IAM: https://console.aws.amazon.com/iam/
2. En el menú lateral, haz clic en "Users" → "Create user"
3. Nombre de usuario: `ai-dj-developer`
4. Marca "Provide user access to the AWS Management Console" (opcional)
5. Haz clic en "Next"
6. Selecciona "Attach policies directly"
7. Busca y marca: `AdministratorAccess` (para desarrollo)
8. Haz clic en "Next" → "Create user"

### 2.3 Crear Access Keys

1. Haz clic en el usuario recién creado
2. Ve a la pestaña "Security credentials"
3. En "Access keys", haz clic en "Create access key"
4. Selecciona "Command Line Interface (CLI)"
5. Marca la confirmación y haz clic en "Next"
6. Añade una descripción (opcional) y haz clic en "Create access key"
7. **IMPORTANTE**: Descarga el archivo CSV o copia las credenciales:
   - Access key ID
   - Secret access key
8. Guárdalas en un lugar seguro (no las compartas)

### 2.4 Configurar AWS CLI

```powershell
aws configure
```

Introduce:
- **AWS Access Key ID**: [Tu Access Key ID]
- **AWS Secret Access Key**: [Tu Secret Access Key]
- **Default region name**: `us-east-1`
- **Default output format**: `json`

Verifica:
```powershell
aws sts get-caller-identity
# Debe mostrar tu Account ID y User ARN
```

### 2.5 Habilitar Amazon Bedrock

1. Ve a: https://console.aws.amazon.com/bedrock/
2. Asegúrate de estar en la región **us-east-1** (esquina superior derecha)
3. En el menú lateral, haz clic en "Model access"
4. Haz clic en "Manage model access" (botón naranja)
5. Busca **Anthropic** y marca:
   - ✅ Claude 3 Sonnet
6. Haz clic en "Request model access"
7. Espera unos segundos (usualmente se aprueba instantáneamente)
8. Verifica que el estado sea "Access granted" (verde)

---

## 3. Configuración de Spotify

### 3.1 Crear Cuenta de Spotify Developer

1. Ve a: https://developer.spotify.com/dashboard
2. Inicia sesión con tu cuenta de Spotify (o crea una)
3. Acepta los términos de servicio

### 3.2 Crear una Aplicación

1. Haz clic en "Create app"
2. Completa el formulario:
   - **App name**: `AI DJ`
   - **App description**: `AI-powered playlist generator`
   - **Redirect URIs**: `http://localhost:8888/callback`
   - **Which API/SDKs are you planning to use?**: Marca "Web API"
3. Acepta los términos y haz clic en "Save"

### 3.3 Obtener Credenciales

1. En el dashboard de tu app, haz clic en "Settings"
2. Verás:
   - **Client ID**: Cópialo
   - **Client Secret**: Haz clic en "View client secret" y cópialo
3. Guarda ambos valores en un lugar seguro

---

## 4. Configuración del Proyecto Local

### 4.1 Clonar el Repositorio

```powershell
# Navegar a tu carpeta de proyectos
cd c:\desarrollo\workspaces\hackaton

# Si el proyecto ya existe
cd ai-dj

# Si necesitas clonarlo desde GitHub
git clone https://github.com/TU_USUARIO/ai-dj.git
cd ai-dj
```

### 4.2 Crear Entorno Virtual

```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.\.venv\Scripts\Activate.ps1
```

**Si obtienes un error de permisos**:
```powershell
# Ejecuta esto primero (como administrador)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Luego intenta activar de nuevo
.\.venv\Scripts\Activate.ps1
```

Deberías ver `(.venv)` al inicio de tu prompt.

### 4.3 Instalar Dependencias

```powershell
# Asegúrate de que el entorno virtual esté activado
# Deberías ver (.venv) en el prompt

# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias del proyecto CDK
pip install -r requirements.txt

# Instalar dependencias de Lambda
cd lambda_src
pip install -r requirements.txt
cd ..
```

### 4.4 Verificar Estructura del Proyecto

```powershell
# Ver estructura
tree /F /A
```

Deberías ver:
```
ai-dj/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── ai_dj/
│   ├── __init__.py
│   └── ai_dj_stack.py
├── lambda_src/
│   ├── __init__.py
│   ├── app.py
│   └── requirements.txt
├── app.py
├── cdk.json
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 5. Configuración de GitHub

### 5.1 Crear Repositorio en GitHub

1. Ve a: https://github.com/new
2. Nombre del repositorio: `ai-dj`
3. Descripción: `AI-powered Spotify playlist generator`
4. Selecciona "Private" o "Public" según prefieras
5. **NO** marques "Initialize this repository with a README"
6. Haz clic en "Create repository"

### 5.2 Conectar Repositorio Local

```powershell
# Si es un nuevo repositorio
git init
git add .
git commit -m "Initial commit: AI DJ serverless app"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/ai-dj.git
git push -u origin main
```

### 5.3 Configurar Secretos en GitHub

1. Ve a tu repositorio en GitHub
2. Haz clic en **Settings** (pestaña superior)
3. En el menú lateral, ve a **Secrets and variables** → **Actions**
4. Haz clic en **New repository secret**

Añade los siguientes secretos uno por uno:

#### Secreto 1: AWS_ACCESS_KEY_ID
- **Name**: `AWS_ACCESS_KEY_ID`
- **Secret**: [Tu AWS Access Key ID del paso 2.3]
- Haz clic en "Add secret"

#### Secreto 2: AWS_SECRET_ACCESS_KEY
- **Name**: `AWS_SECRET_ACCESS_KEY`
- **Secret**: [Tu AWS Secret Access Key del paso 2.3]
- Haz clic en "Add secret"

#### Secreto 3: AWS_ACCOUNT_ID
- **Name**: `AWS_ACCOUNT_ID`
- **Secret**: [Tu AWS Account ID de 12 dígitos]
- Haz clic en "Add secret"

#### Secreto 4: SPOTIFY_CLIENT_ID
- **Name**: `SPOTIFY_CLIENT_ID`
- **Secret**: [Tu Spotify Client ID del paso 3.3]
- Haz clic en "Add secret"

#### Secreto 5: SPOTIFY_CLIENT_SECRET
- **Name**: `SPOTIFY_CLIENT_SECRET`
- **Secret**: [Tu Spotify Client Secret del paso 3.3]
- Haz clic en "Add secret"

### 5.4 Verificar Secretos

Deberías ver 5 secretos listados:
- ✅ AWS_ACCESS_KEY_ID
- ✅ AWS_SECRET_ACCESS_KEY
- ✅ AWS_ACCOUNT_ID
- ✅ SPOTIFY_CLIENT_ID
- ✅ SPOTIFY_CLIENT_SECRET

---

## 6. Primer Despliegue

### 6.1 Opción A: Despliegue Automático (Recomendado)

```powershell
# Asegúrate de que todos los cambios estén commiteados
git status

# Si hay cambios pendientes
git add .
git commit -m "Ready for first deployment"

# Push a main para activar el despliegue
git push origin main
```

### 6.2 Monitorear el Despliegue

1. Ve a tu repositorio en GitHub
2. Haz clic en la pestaña **Actions**
3. Verás el workflow "Deploy AI DJ to AWS" ejecutándose
4. Haz clic en el workflow para ver los detalles
5. Expande cada paso para ver los logs

**Tiempo estimado**: 5-10 minutos

### 6.3 Opción B: Despliegue Local (Opcional)

Si prefieres desplegar desde tu máquina:

```powershell
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Configurar variables de entorno
$env:SPOTIFY_CLIENT_ID = "tu_client_id_aqui"
$env:SPOTIFY_CLIENT_SECRET = "tu_client_secret_aqui"

# Bootstrap (solo primera vez)
cdk bootstrap

# Sintetizar (verificar que no hay errores)
cdk synth

# Desplegar
cdk deploy

# Confirma con 'y' cuando se te pregunte
```

---

## 7. Verificación

### 7.1 Verificar Despliegue Exitoso

En GitHub Actions, el último paso debería mostrar:

```
=== Deployment Outputs ===
{
  "AiDjStack": {
    "ApiEndpoint": "https://abc123xyz.execute-api.us-east-1.amazonaws.com/",
    "DynamoDBTableName": "AI-DJ-Users",
    "LambdaFunctionName": "AI-DJ-Handler"
  }
}
```

### 7.2 Obtener el API Endpoint

**Desde GitHub Actions**:
1. Ve al último workflow exitoso
2. Expande el paso "Display deployment outputs"
3. Copia el valor de `ApiEndpoint`

**Desde AWS Console**:
1. Ve a: https://console.aws.amazon.com/apigateway/
2. Busca "AI-DJ-API"
3. Copia la URL del endpoint

**Desde línea de comandos**:
```powershell
aws cloudformation describe-stacks --stack-name AiDjStack --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" --output text
```

### 7.3 Probar la API (Básico)

```powershell
# Guardar el endpoint en una variable
$API_ENDPOINT = "https://tu-endpoint-aqui.execute-api.us-east-1.amazonaws.com"

# Probar con curl (requiere Spotify access token válido)
curl -X POST "$API_ENDPOINT/playlist" `
  -H "Content-Type: application/json" `
  -d '{
    "user_id": "test_user",
    "prompt": "Música relajante para estudiar",
    "spotify_access_token": "TU_TOKEN_AQUI"
  }'
```

**Nota**: Para obtener un Spotify access token, necesitas implementar OAuth 2.0. Ver documentación de Spotify.

### 7.4 Verificar Recursos en AWS

**Lambda**:
```powershell
aws lambda get-function --function-name AI-DJ-Handler
```

**DynamoDB**:
```powershell
aws dynamodb describe-table --table-name AI-DJ-Users
```

**API Gateway**:
```powershell
aws apigatewayv2 get-apis
```

### 7.5 Ver Logs de Lambda

```powershell
# Ver logs en tiempo real
aws logs tail /aws/lambda/AI-DJ-Handler --follow

# Ver últimos logs
aws logs tail /aws/lambda/AI-DJ-Handler --since 1h
```

---

## 🎉 ¡Felicidades!

Tu aplicación AI DJ está desplegada y funcionando. Ahora cada vez que hagas push a `main`, se desplegará automáticamente.

## 🔄 Próximos Pasos

1. **Implementar autenticación de Spotify**: Crear un flujo OAuth para obtener access tokens
2. **Crear un frontend**: Interfaz web para que los usuarios interactúen con la API
3. **Añadir tests**: Pruebas unitarias y de integración
4. **Monitoreo**: Configurar alarmas en CloudWatch
5. **Optimización**: Ajustar timeouts, memoria, y costos

## 🆘 Solución de Problemas Comunes

### Error: "Unable to locate credentials"
```powershell
# Reconfigurar AWS CLI
aws configure
```

### Error: "Access Denied" en Bedrock
- Verifica que solicitaste acceso al modelo en la consola de Bedrock
- Asegúrate de estar en la región us-east-1

### Error: "Stack already exists"
```powershell
# Eliminar stack existente
cdk destroy
# Luego volver a desplegar
cdk deploy
```

### GitHub Actions falla en "CDK Bootstrap"
- Verifica que los secretos estén configurados correctamente
- Asegúrate de que el usuario IAM tenga permisos de AdministratorAccess

### Error: "Invalid client" en Spotify
- Verifica que el Client ID y Client Secret sean correctos
- Asegúrate de que no haya espacios extra al copiar/pegar

---

## 📞 Recursos Adicionales

- **AWS CDK Docs**: https://docs.aws.amazon.com/cdk/
- **Spotify Web API**: https://developer.spotify.com/documentation/web-api
- **Amazon Bedrock**: https://docs.aws.amazon.com/bedrock/
- **GitHub Actions**: https://docs.github.com/en/actions

---

**¿Necesitas ayuda?** Abre un issue en el repositorio de GitHub.
