# 📡 Ejemplo Completo: Webhook con Dominio Personalizado

## Escenario: Tu pizzería en `api.pizzerianova.com`

### 1️⃣ Arquitectura de Red

```
┌────────────────────────────────────────────────┐
│         INTERNET PÚBLICA                       │
└─────────────┬──────────────────────────────────┘
              │
              │ usuario.telegram.org
              │ POST: https://api.pizzerianova.com/telegram/webhook
              ▼
┌────────────────────────────────────────────────┐
│    Tu Dominio: api.pizzerianova.com            │
│              (HTTPS: 443)                      │
│         CloudFlare / Linode / DigitalOcean    │
└─────────────┬──────────────────────────────────┘
              │
              │ Reverse Proxy (Nginx)
              │ Redirecciona internamente
              ▼
┌────────────────────────────────────────────────┐
│    Tu Servidor (IP privada o localhost)        │
│           Backend Flask:5000                   │
│                                                │
│  POST /telegram/webhook                       │
│  ├─ Validar token secreto                     │
│  ├─ Procesar comando (ej: /start)             │
│  ├─ Guardar pedido en Firebase                │
│  └─ Responder al usuario                      │
└────────────────────────────────────────────────┘
```

---

## 🔧 Setup Paso a Paso

### Paso 1: Ejecutar Script de Configuración

```powershell
# Windows PowerShell
python setup_webhook.py

# Selecciona opción 2 (Dominio personalizado)
# Ingresa: api.pizzerianova.com
# Ingresa: token_secreto_super_seguro_1234567890
```

Esto genera `pizzeria_backend/.env`:
```
USE_WEBHOOK=true
WEBHOOK_URL=https://api.pizzerianova.com
WEBHOOK_SECRET_TOKEN=token_secreto_super_seguro_1234567890
```

### Paso 2: Configurar el Servidor (Ejemplo: DigitalOcean)

```bash
# 1. Conectar a tu servidor
ssh root@tu.ip.publica

# 2. Instalar Nginx
apt update
apt install nginx

# 3. Crear archivo de configuración
nano /etc/nginx/sites-available/pizzeria-bot
```

**Contenido del archivo nginx**:
```nginx
server {
    listen 443 ssl http2;
    server_name api.pizzerianova.com;

    # SSL con Let's Encrypt
    ssl_certificate /etc/letsencrypt/live/api.pizzerianova.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.pizzerianova.com/privkey.pem;

    location /telegram/webhook {
        proxy_pass http://127.0.0.1:5000/telegram/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name api.pizzerianova.com;
    return 301 https://$server_name$request_uri;
}
```

Continuar setup:
```bash
# 4. Habilitar sitio
ln -s /etc/nginx/sites-available/pizzeria-bot /etc/nginx/sites-enabled/

# 5. Generar certificado SSL (Let's Encrypt)
apt install certbot python3-certbot-nginx
certbot certonly --nginx -d api.pizzerianova.com

# 6. Probar configuración nginx
nginx -t

# 7. Reiniciar nginx
systemctl restart nginx
```

### Paso 3: Actualizar DNS

En tu proveedor de dominio (GoDaddy, Namecheap, etc.):

```
Tipo:  A
Nombre: api
Valor:  tu.ip.publica.aqui
TTL:   3600
```

Esperar ~5-10 minutos a que se propague.

### Paso 4: Desplegar Backend

```bash
# En el servidor, descargar código
cd /opt/pizzeria-bot
git clone https://github.com/tuuser/Bot_TelegramIHC.git
cd Bot_TelegramIHC/pizzeria_backend

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env (desde tu máquina local)
# Copiar el .env generado en setup_webhook.py
scp .env root@tu.ip.publica:/opt/pizzeria-bot/pizzeria_backend/

# Ejecutar backend (con systemd para que se mantenga activo)
```

### Paso 5: Mantener Backend Activo (Systemd)

Crear `/etc/systemd/system/pizzeria-bot.service`:

```ini
[Unit]
Description=Pizzeria Bot Telegram
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pizzeria-bot/pizzeria_backend
ExecStart=/usr/bin/python3 /opt/pizzeria-bot/pizzeria_backend/run.py
Restart=always
RestartSec=10

Environment="PYTHONUNBUFFERED=1"
Environment="USE_WEBHOOK=true"

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
systemctl enable pizzeria-bot
systemctl start pizzeria-bot
systemctl status pizzeria-bot
```

---

## ✅ Verificar que Todo Funciona

### 1. Verificar webhook registrado en Telegram

```python
# Script: test_webhook.py
from telegram import Bot
import asyncio
import os

async def check():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    info = await bot.get_webhook_info()
    print(f"URL: {info.url}")
    print(f"Pending: {info.pending_update_count}")
    print(f"Last Error: {info.last_error_date}")

asyncio.run(check())
```

Output esperado:
```
URL: https://api.pizzerianova.com/telegram/webhook
Pending: 0
Last Error: None
```

### 2. Probar endpoint con curl

```bash
curl -X POST https://api.pizzerianova.com/telegram/webhook \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: token_secreto_super_seguro_1234567890" \
  -d '{
    "update_id": 123,
    "message": {
      "message_id": 1,
      "chat": {"id": 123456789},
      "text": "/start"
    }
  }'
```

Expected response:
```json
{"status": "ok"}
```

### 3. Revisar logs del backend

```bash
# Ver logs en tiempo real
tail -f /var/log/pizzeria-bot.log

# O si usas systemd
journalctl -u pizzeria-bot -f
```

---

## 🎯 Flujo Completo de un Pedido

```
1. Usuario abre Telegram
   └─→ Envía /start

2. Telegram detecta comando
   └─→ POST https://api.pizzerianova.com/telegram/webhook
       {
         "update_id": 123,
         "message": {
           "chat": {"id": 999},
           "text": "/start"
         }
       }

3. Nginx recibe request
   └─→ Redirige a http://127.0.0.1:5000/telegram/webhook

4. Backend procesa
   └─→ Valida token secreto ✅
   └─→ Ejecuta handler /start
   └─→ Responde con WebApp link

5. Usuario hace pedido en WebApp
   └─→ POST https://api.pizzerianova.com/submit_order
   └─→ Backend guarda en Firebase
   └─→ Envía notificación a cliente y restaurante

6. Admin actualiza estado
   └─→ POST https://api.pizzerianova.com/update_status/order_id
   └─→ Backend notifica cliente instantáneamente
```

---

## 🔐 Seguridad en Producción

✅ **HTTPS obligatorio**: Telegram valida certificado
✅ **Token secreto**: Único y fuerte
✅ **Firewall**: Solo puertos 80, 443
✅ **Variables de entorno**: No hardcodees credenciales
✅ **Auto-renovación SSL**: Certbot lo hace automáticamente
✅ **Rate limiting**: Nginx protege contra ataques

---

## 📊 Comparativa: ngrok vs Dominio Personalizado

| Feature | ngrok | Dominio |
|---------|-------|---------|
| **Setup** | 5 min | 30 min |
| **Costo** | Gratis | $10-15/año + VPS |
| **Permanencia** | ⚠️ URL cambia | ✅ Permanente |
| **Producción** | ❌ No | ✅ Sí |
| **Escalabilidad** | Limitada | Excelente |
| **Confiabilidad** | 99% | 99.9% |
| **Recomendado** | Dev/Test | Producción |

---

## 🚀 Servicios Recomendados

### 1. **DigitalOcean** (Recomendado)
- Droplet $5/mes
- 1GB RAM, 25GB SSD
- Perfecto para este proyecto

### 2. **Render.com** (Más Fácil)
- Deployment automático desde GitHub
- HTTPS gratuito
- URL personalizada

### 3. **Railway.app**
- Similar a Render
- Muy fácil de usar

### 4. **CloudFlare Pages + Workers**
- Soporte serverless
- CDN global
- Gratuito

---

**¿Necesitas ayuda para configurar en algún servicio específico?**
