# 🎵 Configuración de Spotify para el Hackathon

## ⚠️ Problema: Solo funciona con tu cuenta de Spotify

Tu aplicación de Spotify está en **Modo Development (Desarrollo)**, lo cual limita el acceso solo a usuarios en la whitelist.

---

## 🔓 Solución 1: Modo Development + Agregar usuarios

Si quieres mantener el modo Development para el hackathon, puedes agregar hasta **25 usuarios** a la whitelist:

### Pasos:
1. Ve a: https://developer.spotify.com/dashboard
2. Selecciona tu app "AI DJ"
3. Ve a **Settings**
4. Busca la sección **"User Management"**
5. Click en **"Add User"**
6. Ingresa el **nombre** y **email** de cada usuario que quieras que pruebe tu app
7. Los usuarios recibirán un email de invitación (opcional)

**Usuarios para agregar (jueces del hackathon):**
- Agrega los emails de los jueces si los tienes
- Agrega amigos/testers para la demo

---

## ✅ Solución 2: Solicitar Modo Extended Quota (Recomendado para hackathon)

### Pasos para Extended Quota:
1. Ve a: https://developer.spotify.com/dashboard
2. Selecciona tu app "AI DJ"
3. Click en **"Request Extension"** o **"Quota Extension"**
4. Llena el formulario explicando:
   - **Nombre**: AI DJ
   - **Descripción**: "AI-powered playlist generator for AWS AI Agent Hackathon"
   - **Company/Organization**: Tu nombre o "Independent Developer"
   - **Website**: `https://d1z4qoq01pmvv3.cloudfront.net`
   - **Razón**: "AWS AI Agent Global Hackathon demonstration. Need public access for judges and demo."

**Tiempo de aprobación**: 3-7 días (no ideal para hackathon)

---

## 🚀 Solución 3: Modo Production (Requiere verificación)

Para acceso completamente público necesitas:
1. Completar verificación de Spotify
2. Agregar políticas de privacidad
3. Agregar términos de servicio

**No recomendado para el hackathon** (toma mucho tiempo)

---

## 💡 Recomendación para el Hackathon

**Usa Solución 1 (User Management)**:

### Agrega estos usuarios a tu whitelist:
1. **Tu cuenta** (ya está)
2. **Cuenta de prueba 1**: Crea una cuenta secundaria de Spotify
3. **Jueces**: Si tienes sus emails
4. **Backup**: Tu email personal adicional

### Para la demo en video:
- ✅ Usa tu cuenta principal (que ya funciona)
- ✅ Muestra el flujo completo
- ✅ Menciona que está en "Development mode for security"

### Para jueces en vivo:
1. Agrega sus emails a la whitelist
2. O comparte tu cuenta de prueba (no recomendado)
3. O usa la demo en video

---

## 🎥 Configuración actual

**Redirect URIs configurados:**
```
https://d1z4qoq01pmvv3.cloudfront.net/
```

**Scopes usados:**
- `user-read-private`
- `user-read-email`
- `playlist-modify-public`
- `playlist-modify-private`

**Estado actual:** ✅ Funcionando correctamente para usuarios en whitelist

---

## 📝 Nota en la documentación

Agrega esto a tu README o submission:

```
**Note about Spotify Authentication:**
Due to Spotify's development mode restrictions, the application 
currently requires whitelisted users. For hackathon judges who 
want to test the application, please contact me to add your 
email to the whitelist. Alternatively, you can view the full 
demo in the provided video.
```

---

## ✅ Checklist para el Hackathon

- [ ] Agregar al menos 3 usuarios de prueba a la whitelist
- [ ] Crear demo video usando tu cuenta (que funciona)
- [ ] Agregar nota en README sobre la limitación de Development mode
- [ ] Preparar cuenta de prueba para compartir (opcional)
- [ ] Tener los access tokens listos para la demo

---

## 🔗 Links útiles

- **Spotify Dashboard**: https://developer.spotify.com/dashboard
- **User Management**: https://developer.spotify.com/dashboard → Tu App → Settings → User Management
- **Docs sobre Quotas**: https://developer.spotify.com/documentation/web-api/concepts/quota-modes

---

**La app funciona perfectamente, solo está limitada por seguridad de Spotify en modo Development.**
