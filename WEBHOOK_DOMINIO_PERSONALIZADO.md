# 🌐 Webhook con Dominio HTTPS Personalizado

## Opción: Usar tu Propio Dominio (Producción)

Si tienes un dominio personalizado (ej: `www.tudominio.com` o `api.pizzeria.com`), puedes configurar el webhook directamente sin ngrok.

---

## 📋 Requisitos

1. **Dominio personalizado** (ej: `tu-dominio.com`)
2. **Certificado SSL válido** (HTTPS)
3. **Servidor con IP pública**
4. **Backend deployado** en un servidor real

---

## 🔧 Configuración Paso a Paso

### Paso 1: Actualizar `config.py`

```python
# config.py
import os

BOT_TOKEN = "8334575884:AAEivWr_jKwAQ3qAC2aSc569OJeyY0MCom4"

# --- WEBHOOK TELEGRAM CON DOMINIO PERSONALIZADO ---
# Usar tu propio dominio en lugar de ngrok
WEBHOOK_URL = os.environ.get(
    "WEBHOOK_URL", 
    "https://tu-dominio.com"  # ⚠️ CAMBIA ESTO A TU DOMINIO
)

WEBHOOK_PATH = "/telegram/webhook"
WEBHOOK_SECRET_TOKEN = os.environ.get(
    "WEBHOOK_SECRET_TOKEN", 
    "tu_token_secreto_aqui_123456"
)
```

### Paso 2: Flujo de Configuración

```
Tu Dominio (HTTPS)
    ↓
tu-dominio.com:443 (Puerto HTTPS)
    ↓
Tu Servidor (Reverse Proxy - Nginx/Apache)
    ↓
Backend Flask (Puerto 5000 interno)
    ↓
Endpoint: /telegram/webhook
```

### Paso 3: Configurar Nginx (Recomendado)

Si usas **Nginx** como reverse proxy:

```nginx
# /etc/nginx/sites-available/telegram-bot

server {
    listen 443 ssl http2;
    server_name tu-dominio.com;

    # Certificado SSL (Let's Encrypt o similar)
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;

    # Seguridad SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location /telegram/webhook {
        proxy_pass http://localhost:5000/telegram/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirigir HTTP a HTTPS
server {
    listen 80;
    server_name tu-dominio.com;
    return 301 https://$server_name$request_uri;
}
```

### Paso 4: Configurar Apache (Alternativa)

Si prefieres **Apache**:

```apache
# /etc/apache2/sites-available/telegram-bot.conf

<VirtualHost *:443>
    ServerName tu-dominio.com
    ServerAlias www.tu-dominio.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/tu-dominio.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/tu-dominio.com/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/

    # Header específico para webhook
    <Location /telegram/webhook>
        ProxyPass http://localhost:5000/telegram/webhook
        ProxyPassReverse http://localhost:5000/telegram/webhook
    </Location>
</VirtualHost>

<VirtualHost *:80>
    ServerName tu-dominio.com
    Redirect permanent / https://tu-dominio.com/
</VirtualHost>
```

---

## 🚀 Obtener Certificado SSL (Gratuito)

### Opción 1: Let's Encrypt (Recomendado)

```bash
# Instalar Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generar certificado
sudo certbot certonly --nginx -d tu-dominio.com

# Auto-renovación
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Opción 2: CloudFlare (Más Fácil)

1. Registro en https://cloudflare.com
2. Apunta tu dominio a Cloudflare
3. Cloudflare proporciona SSL/TLS automáticamente
4. Tu DNS apunta a Cloudflare
5. Cloudflare redirige a tu IP pública

---

## 🔄 Iniciar Backend con Dominio

### Método 1: Variables de Entorno

```bash
# Linux/Mac
export WEBHOOK_URL="https://tu-dominio.com"
export WEBHOOK_SECRET_TOKEN="token_muy_secreto_aqui"
export USE_WEBHOOK="true"

cd pizzeria_backend
python run.py
```

```powershell
# Windows PowerShell
$env:WEBHOOK_URL = "https://tu-dominio.com"
$env:WEBHOOK_SECRET_TOKEN = "token_muy_secreto_aqui"
$env:USE_WEBHOOK = "true"

cd pizzeria_backend
python run.py
```

### Método 2: Archivo `.env`

```bash
# pizzeria_backend/.env
WEBHOOK_URL=https://tu-dominio.com
WEBHOOK_SECRET_TOKEN=token_muy_secreto_aqui
USE_WEBHOOK=true
BOT_TOKEN=8334575884:AAEivWr_jKwAQ3qAC2aSc569OJeyY0MCom4
```

Luego en `config.py`:
```python
from dotenv import load_dotenv
load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://localhost:5000")
```

---

## 📊 Arquitectura Final

```
┌─────────────────────────────────────────┐
│         Usuario en Telegram             │
│    /start → Toca botón → Mensaje        │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│        Servidores de Telegram           │
│     (API de Telegram en la nube)        │
└─────────────┬───────────────────────────┘
              │
              │ POST /telegram/webhook
              │ (HTTPS)
              ▼
┌─────────────────────────────────────────┐
│        tu-dominio.com:443               │
│     (Tu Servidor Web HTTPS)             │
│  (Nginx/Apache - Reverse Proxy)         │
└─────────────┬───────────────────────────┘
              │
              │ (Redirige internamente)
              ▼
┌─────────────────────────────────────────┐
│    Backend Flask (localhost:5000)       │
│  /telegram/webhook                      │
│  ├─ Valida token secreto                │
│  ├─ Procesa update                      │
│  ├─ Guarda en Firebase                  │
│  └─ Responde al usuario                 │
└─────────────────────────────────────────┘
```

---

## ✅ Verificar que Funciona

### 1. Verificar que el webhook está registrado:

```python
# Script para verificar
from telegram import Bot
import asyncio

async def check_webhook():
    bot = Bot(token="TU_BOT_TOKEN")
    webhook_info = await bot.get_webhook_info()
    print(webhook_info)
    
asyncio.run(check_webhook())
```

Debería mostrar algo como:
```
url=https://tu-dominio.com/telegram/webhook
has_custom_certificate=False
pending_update_count=0
```

### 2. Probar el webhook manualmente:

```bash
# Enviar un update de prueba
curl -X POST https://tu-dominio.com/telegram/webhook \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: tu_token_secreto_aqui_123456" \
  -d '{
    "update_id": 1,
    "message": {
      "message_id": 1,
      "chat": {"id": 123456789, "type": "private"},
      "text": "/start"
    }
  }'
```

---

## 🎯 Opciones de Deployment

### 1. **Render.com** (Recomendado - Fácil)
```bash
# Conecta tu repo GitHub
# Automáticamente:
# - Despliega tu código
# - Proporciona HTTPS
# - Subdominio: https://pizza-bot-production.onrender.com
```

### 2. **Railway.app**
```bash
# Similar a Render
# - HTTPS automático
# - URL pública
```

### 3. **Heroku** (Ya no es gratuito)
```bash
# Antes era gratuito, ahora requiere pago
```

### 4. **DigitalOcean/Linode**
```bash
# Servidor VPS propio
# - Control total
# - Certificado SSL (Let's Encrypt)
# - Nginx/Apache configurados
```

---

## 🔐 Seguridad

✅ **Token Secreto**: Cambia el valor por defecto
✅ **HTTPS obligatorio**: Nunca uses HTTP
✅ **Firewall**: Abre solo puertos 80 y 443
✅ **Variables de entorno**: No hardcodees credenciales

---

## 📝 Resumen

| Aspecto | ngrok | Dominio HTTPS |
|--------|-------|---------------|
| **Producción** | ❌ No | ✅ Sí |
| **Estabilidad** | ⚠️ URL cambia | ✅ Permanente |
| **Costo** | Gratuito | Dominio ($10-15/año) |
| **Setup** | Fácil | Moderado |
| **Escalabilidad** | Limitada | Excelente |
| **Recomendado** | Desarrollo | Producción |

---

**¿Quieres ayuda para deployar en algún servicio específico?**
