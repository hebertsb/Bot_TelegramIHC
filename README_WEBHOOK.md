# 🍕 Pizzeria Bot - Guía de Webhook

## 📌 Resumen Rápido

Tu bot de Telegram puede conectarse de **3 formas diferentes**:

| Método | Uso | Setup | Costo |
|--------|-----|-------|-------|
| 🚀 **ngrok** | Desarrollo rápido | 2 minutos | Gratis |
| 🌐 **Dominio HTTPS** | Producción real | 30 minutos | $10/año |
| 📡 **Polling** | Testing local | 1 minuto | Gratis |

---

## 🎯 Elige tu Método

### ✅ Opción 1: ngrok (Recomendado para DEV)

**Ideal para**: Desarrollo, testing, prototipado rápido

**Ventajas**:
- ✅ Setup en 2 minutos
- ✅ Sin certificados SSL
- ✅ Sin servidor propio
- ✅ URL pública automática

**Desventajas**:
- ⚠️ URL cambia cada reinicio
- ⚠️ No para producción
- ⚠️ Límites de ancho de banda

**Cómo usar**:
```powershell
# Windows PowerShell
.\start_with_webhook.ps1
```

👉 **Más info**: Ver `WEBHOOK_SETUP.md`

---

### ✅ Opción 2: Dominio HTTPS Personalizado (Recomendado para PROD)

**Ideal para**: Producción, aplicación en vivo, clientes reales

**Ventajas**:
- ✅ URL permanente (tu dominio)
- ✅ Profesional
- ✅ Escalable
- ✅ Control total

**Desventajas**:
- ❌ Requiere dominio propio
- ❌ Requiere servidor o VPS
- ❌ Setup más complejo

**Cómo usar**:
```bash
# 1. Ejecutar configurador
python setup_webhook.py

# 2. Seleccionar opción 2
# 3. Ingresar dominio y token

# 4. Iniciar backend
cd pizzeria_backend
python run.py
```

👉 **Más info**: 
- `WEBHOOK_DOMINIO_PERSONALIZADO.md`
- `EJEMPLO_DOMINIO_COMPLETO.md`

---

### ✅ Opción 3: Polling Local (Para testing)

**Ideal para**: Testing, sin internet público

**Ventajas**:
- ✅ Funciona detrás de firewall
- ✅ Sin certificados
- ✅ Desarrollo local

**Desventajas**:
- ❌ Lento (30s de delay)
- ❌ Alto consumo de CPU
- ❌ No escalable

**Cómo usar**:
```bash
python setup_webhook.py
# Seleccionar opción 3

cd pizzeria_backend
python run.py
```

---

## 🚀 Instalación Rápida

### 1️⃣ Actualizar dependencias

```bash
pip install -r pizzeria_backend/requirements.txt
```

### 2️⃣ Configurar webhook

```bash
# Ejecutar asistente interactivo
python setup_webhook.py
```

O configurar manualmente con variables de entorno:

```powershell
# Para ngrok (automático)
$env:USE_WEBHOOK = "true"
python pizzeria_backend/run.py

# Para dominio personalizado
$env:USE_WEBHOOK = "true"
$env:WEBHOOK_URL = "https://tu-dominio.com"
$env:WEBHOOK_SECRET_TOKEN = "token_secreto_aqui"
python pizzeria_backend/run.py

# Para polling
$env:USE_WEBHOOK = "false"
python pizzeria_backend/run.py
```

---

## 📁 Estructura de Archivos

```
Bot_TelegramIHC/
├── pizzeria_backend/
│   ├── .env                    # Variables de entorno (generado)
│   ├── config.py               # Configuración
│   ├── run.py                  # Punto de entrada (webhook + bot)
│   ├── requirements.txt         # Dependencias
│   └── app/
│       ├── routes.py           # Endpoints (incluyendo /telegram/webhook)
│       ├── services.py         # Lógica de Firebase
│       └── bot.py              # Handlers del bot
│
├── setup_webhook.py            # ⭐ Configurador asistente
├── start_with_webhook.ps1      # Script PowerShell
├── start_with_webhook.bat      # Script Batch
│
├── WEBHOOK_SETUP.md            # Guía ngrok
├── WEBHOOK_DOMINIO_PERSONALIZADO.md  # Guía dominio
└── EJEMPLO_DOMINIO_COMPLETO.md      # Ejemplo paso a paso
```

---

## 🔍 Verificar que Funciona

### Método 1: Logs

```bash
# En los logs deberías ver:
# ✅ "Bot setup completed"
# ✅ "Webhook configured successfully"
# ✅ "Ready to receive updates"
```

### Método 2: Test Script

```python
# test_webhook.py
from telegram import Bot
import asyncio
import os

async def check():
    bot = Bot(token="tu_bot_token")
    info = await bot.get_webhook_info()
    print(f"✅ Webhook URL: {info.url}")
    print(f"✅ Updates pendientes: {info.pending_update_count}")

asyncio.run(check())
```

### Método 3: Enviar comando a tu bot

1. Abre Telegram
2. Busca tu bot
3. Envía `/start`
4. Deberías ver la respuesta instantáneamente

---

## 🐛 Problemas Comunes

### "ngrok no encontrado"
```
Solución: Instala ngrok desde https://ngrok.com
```

### "Webhook no recibe updates"
```
Solución:
1. Verifica que la URL en config.py es correcta
2. Comprueba certificado SSL (HTTPS)
3. Revisa token secreto
4. Mira los logs del backend
```

### "Error: WEBHOOK_URL inválida"
```
Solución: Asegúrate que incluye https:// o http://
```

### "Cambiar entre métodos"
```
python setup_webhook.py
# Selecciona otra opción y regenera .env
```

---

## 📊 Decisión Rápida

**¿Estás en desarrollo?** → Usa **ngrok** (opción 1)

**¿Quieres producción real?** → Usa **Dominio HTTPS** (opción 2)

**¿Solo testing local?** → Usa **Polling** (opción 3)

---

## 🌐 Servicios Recomendados para Dominio

- **Dominio**: GoDaddy, Namecheap, Porkbun (~$10/año)
- **Servidor VPS**: DigitalOcean, Linode, Vultr ($5-10/mes)
- **Deploy fácil**: Render.com, Railway.app (HTTPS automático)
- **SSL gratis**: Let's Encrypt (automático con Certbot)

---

## 📞 Documentación

- **ngrok**: `WEBHOOK_SETUP.md`
- **Dominio personalizado**: `WEBHOOK_DOMINIO_PERSONALIZADO.md`
- **Ejemplo completo**: `EJEMPLO_DOMINIO_COMPLETO.md`

---

## ✨ Características del Sistema

✅ **Inteligente**: Detecta automáticamente método disponible
✅ **Flexible**: Fácil cambiar entre métodos
✅ **Seguro**: Token secreto validado
✅ **Fallback**: Si webhook falla, cambia a polling
✅ **Logs detallados**: Sabe exactamente qué está pasando

---

**Listo para empezar? 🚀**

```bash
python setup_webhook.py
```
