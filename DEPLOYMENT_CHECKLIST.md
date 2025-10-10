# ✅ Checklist de Despliegue - AI DJ

Usa esta lista para asegurarte de que todo está configurado correctamente antes del despliegue.

## Pre-Despliegue

### Software Instalado

- [ ] Python 3.12+ instalado
  ```powershell
  python --version
  ```

- [ ] Node.js 20+ instalado
  ```powershell
  node --version
  ```

- [ ] AWS CLI instalado y configurado
  ```powershell
  aws --version
  aws sts get-caller-identity
  ```

- [ ] AWS CDK instalado
  ```powershell
  cdk --version
  ```

- [ ] Git instalado
  ```powershell
  git --version
  ```

### Cuentas y Credenciales

- [ ] Cuenta de AWS activa
- [ ] AWS Access Key ID y Secret Access Key creados
- [ ] AWS CLI configurado con credenciales
  ```powershell
  aws configure list
  ```

- [ ] Amazon Bedrock habilitado en us-east-1
- [ ] Acceso a Claude 3 Sonnet aprobado en Bedrock
  - Verificar en: https://console.aws.amazon.com/bedrock/ → Model access

- [ ] Spotify Developer App creada
- [ ] Spotify Client ID obtenido
- [ ] Spotify Client Secret obtenido
- [ ] Redirect URIs configurados en Spotify

- [ ] Repositorio de GitHub creado
- [ ] Acceso de escritura al repositorio

### Configuración Local

- [ ] Proyecto clonado/descargado
- [ ] Entorno virtual de Python creado
  ```powershell
  python -m venv .venv
  ```

- [ ] Entorno virtual activado
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

- [ ] Dependencias CDK instaladas
  ```powershell
  pip install -r requirements.txt
  ```

- [ ] Dependencias Lambda instaladas
  ```powershell
  cd lambda_src
  pip install -r requirements.txt
  cd ..
  ```

## Despliegue Local (Opcional)

- [ ] Variables de entorno configuradas
  ```powershell
  $env:SPOTIFY_CLIENT_ID = "tu_client_id"
  $env:SPOTIFY_CLIENT_SECRET = "tu_client_secret"
  ```

- [ ] CDK Bootstrap ejecutado (solo primera vez)
  ```powershell
  cdk bootstrap
  ```

- [ ] CDK Synth ejecutado sin errores
  ```powershell
  cdk synth
  ```

- [ ] CDK Deploy ejecutado exitosamente
  ```powershell
  cdk deploy
  ```

- [ ] API Endpoint obtenido del output
- [ ] Lambda Function verificada en AWS Console
- [ ] DynamoDB Table verificada en AWS Console
- [ ] API Gateway verificado en AWS Console

## Configuración de GitHub

### Repositorio

- [ ] Código subido a GitHub
  ```powershell
  git init
  git add .
  git commit -m "Initial commit"
  git branch -M main
  git remote add origin https://github.com/TU_USUARIO/ai-dj.git
  git push -u origin main
  ```

### Secretos de GitHub Actions

Ir a: Settings → Secrets and variables → Actions → New repository secret

- [ ] `AWS_ACCESS_KEY_ID` configurado
- [ ] `AWS_SECRET_ACCESS_KEY` configurado
- [ ] `AWS_ACCOUNT_ID` configurado (12 dígitos)
- [ ] `SPOTIFY_CLIENT_ID` configurado
- [ ] `SPOTIFY_CLIENT_SECRET` configurado

### Verificación de Secretos

- [ ] 5 secretos listados en GitHub
- [ ] Nombres de secretos sin errores tipográficos
- [ ] Valores copiados correctamente (sin espacios extra)

## Primer Despliegue Automático

- [ ] Push a rama main realizado
  ```powershell
  git push origin main
  ```

- [ ] Workflow de GitHub Actions iniciado
  - Verificar en: Repositorio → Actions

- [ ] Workflow completado exitosamente (✓ verde)
- [ ] Todos los pasos del workflow pasaron
- [ ] API Endpoint visible en los outputs del workflow

## Verificación Post-Despliegue

### Recursos AWS

- [ ] Lambda Function existe
  ```powershell
  aws lambda get-function --function-name AI-DJ-Handler
  ```

- [ ] DynamoDB Table existe
  ```powershell
  aws dynamodb describe-table --table-name AI-DJ-Users
  ```

- [ ] API Gateway existe
  ```powershell
  aws apigatewayv2 get-apis
  ```

- [ ] CloudWatch Log Group existe
  ```powershell
  aws logs describe-log-groups --log-group-name-prefix /aws/lambda/AI-DJ-Handler
  ```

### Permisos IAM

- [ ] Lambda tiene permisos para DynamoDB
- [ ] Lambda tiene permisos para Bedrock
- [ ] Lambda tiene permisos para CloudWatch Logs

Verificar en: AWS Console → Lambda → AI-DJ-Handler → Configuration → Permissions

### Prueba de API

- [ ] API Endpoint responde (aunque sea con error de auth)
  ```powershell
  curl -X POST "https://tu-endpoint/playlist" -H "Content-Type: application/json" -d '{}'
  ```

- [ ] Respuesta recibida (200, 400, o 500)
- [ ] Headers CORS presentes en respuesta

### Logs y Monitoreo

- [ ] Logs de Lambda visibles en CloudWatch
  ```powershell
  aws logs tail /aws/lambda/AI-DJ-Handler --since 1h
  ```

- [ ] No hay errores críticos en logs
- [ ] Métricas de Lambda visibles en CloudWatch

## Prueba End-to-End (Requiere Spotify Token)

- [ ] Spotify Access Token obtenido (ver SPOTIFY_AUTH_GUIDE.md)
- [ ] Petición POST a /playlist exitosa
- [ ] Playlist creada en Spotify
- [ ] Playlist URL devuelta en respuesta
- [ ] Registro guardado en DynamoDB
  ```powershell
  aws dynamodb get-item --table-name AI-DJ-Users --key '{"user_id":{"S":"test_user"}}'
  ```

## Configuración de Producción (Opcional)

### Seguridad

- [ ] API Gateway con autenticación configurada (API Key, Cognito, etc.)
- [ ] Rate limiting configurado
- [ ] WAF configurado (si es necesario)
- [ ] Secrets Manager para credenciales sensibles

### Monitoreo

- [ ] CloudWatch Alarms configuradas
  - Lambda Errors > 5%
  - API Gateway 5XX > 1%
  - Lambda Duration > 50s
  - DynamoDB Throttled Requests > 0

- [ ] SNS Topic para notificaciones
- [ ] Email/SMS configurado para alarmas

### Optimización

- [ ] Lambda memory size ajustado según uso
- [ ] Lambda timeout ajustado según necesidad
- [ ] DynamoDB capacity mode revisado (on-demand vs provisioned)
- [ ] API Gateway caching habilitado (si aplica)

### Backup y Recuperación

- [ ] DynamoDB Point-in-time Recovery habilitado
- [ ] Backups automáticos configurados
- [ ] Plan de recuperación ante desastres documentado

## Documentación

- [ ] README.md actualizado con endpoint real
- [ ] API_DOCUMENTATION.md revisado
- [ ] ARCHITECTURE.md actualizado si hubo cambios
- [ ] Ejemplos de uso documentados
- [ ] Troubleshooting guide actualizado

## Comunicación

- [ ] Equipo notificado del despliegue
- [ ] Documentación compartida
- [ ] Credenciales de acceso distribuidas (si aplica)
- [ ] Calendario de mantenimiento comunicado

## Rollback Plan

- [ ] Procedimiento de rollback documentado
  ```powershell
  # Opción 1: Revertir commit y re-desplegar
  git revert HEAD
  git push
  
  # Opción 2: Destruir y re-desplegar versión anterior
  cdk destroy
  git checkout <commit_anterior>
  cdk deploy
  ```

- [ ] Backup de configuración anterior guardado
- [ ] Contactos de emergencia identificados

## Checklist de Mantenimiento Continuo

### Semanal

- [ ] Revisar logs de errores en CloudWatch
- [ ] Verificar métricas de uso
- [ ] Revisar costos en AWS Cost Explorer

### Mensual

- [ ] Actualizar dependencias de Python
  ```powershell
  pip list --outdated
  ```

- [ ] Actualizar AWS CDK
  ```powershell
  npm update -g aws-cdk
  ```

- [ ] Revisar y optimizar costos
- [ ] Revisar políticas de IAM (principio de menor privilegio)

### Trimestral

- [ ] Revisar arquitectura y escalabilidad
- [ ] Actualizar documentación
- [ ] Realizar pruebas de carga
- [ ] Revisar plan de recuperación ante desastres

## Notas

**Fecha de despliegue**: _______________

**Desplegado por**: _______________

**Versión desplegada**: _______________

**API Endpoint**: _______________

**Región AWS**: _______________

**Observaciones**:
_______________________________________________
_______________________________________________
_______________________________________________

## Problemas Encontrados

| Problema | Solución | Fecha |
|----------|----------|-------|
|          |          |       |
|          |          |       |
|          |          |       |

## Contactos de Soporte

- **AWS Support**: https://console.aws.amazon.com/support/
- **GitHub Support**: https://support.github.com/
- **Spotify Developer**: https://developer.spotify.com/support/
- **Equipo interno**: _______________

---

**Estado del Despliegue**: ⬜ Pendiente | ⬜ En Progreso | ⬜ Completado | ⬜ Fallido

**Aprobado por**: _______________

**Firma**: _______________
