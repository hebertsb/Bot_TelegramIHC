# 🚀 Guía de Implementación: Webhook con ngrok

## Resumen de cambios

He implementado soporte para **Webhook** en tu bot de Telegram usando **ngrok**. El sistema es inteligente y puede funcionar en dos modos:

### ✅ Modo Webhook (Recomendado - Más rápido)
- Telegram empuja updates directamente a tu servidor
- Instantáneo (sin delay)
- Más eficiente con recursos

### 📡 Modo Polling (Fallback)
- Si ngrok no está disponible, automáticamente cambia a polling
- Funciona detrás de firewalls
- No requiere URL pública

---

## 📁 Cambios Realizados

### 1. **config.py**
```python
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://localhost:5000")
WEBHOOK_PATH = "/telegram/webhook"
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN", "tu_token_secreto_aqui")
```

### 2. **app/routes.py**
- ✅ Agregado endpoint `POST /telegram/webhook` que recibe updates de Telegram
- ✅ Validación de token secreto para mayor seguridad
- ✅ Procesamiento de updates en el webhook

### 3. **run.py**
- ✅ `run_telegram_bot_webhook()` - Configura modo webhook
- ✅ `run_telegram_bot_polling()` - Fallback a polling si falla webhook
- ✅ `get_ngrok_url()` - Obtiene URL dinámicamente de ngrok
- ✅ `start_ngrok()` - Inicia ngrok automáticamente
- ✅ Variables de entorno para control flexible

### 4. **Scripts de inicio**
- ✅ `start_with_webhook.ps1` - Script PowerShell para Windows
- ✅ `start_with_webhook.bat` - Script Batch para Windows

### 5. **requirements.txt**
- ✅ Agregada dependencia `requests` para obtener URL de ngrok

---

## 🎯 Cómo usar

### Opción 1: Usar Script (Más Fácil) 🟢

#### En PowerShell:
```powershell
# Cambiar a la carpeta del proyecto
cd "D:\Universidad\Prácticos\Séptimo Semestre\IHC\Proyecto III\Bot_TelegramIHC"

# Ejecutar el script
.\start_with_webhook.ps1
```

#### En CMD (Windows):
```cmd
cd "D:\Universidad\Prácticos\Séptimo Semestre\IHC\Proyecto III\Bot_TelegramIHC"
start_with_webhook.bat
```

### Opción 2: Manual (Si prefieres control)

#### Terminal 1 - Iniciar ngrok:
```bash
ngrok http 5000
```
Espera y anota la URL pública (ej: `https://abc123.ngrok.io`)

#### Terminal 2 - Iniciar Backend:
```powershell
cd pizzeria_backend
$env:USE_WEBHOOK = "true"
$env:NGROK_URL = "https://abc123.ngrok.io"  # Usa tu URL de ngrok
python run.py
```

### Opción 3: Modo Polling (Sin ngrok)
```powershell
cd pizzeria_backend
$env:USE_WEBHOOK = "false"
python run.py
```

---

## 🔧 Instalación de ngrok (Si no lo tienes)

### Windows:
1. Descarga desde: https://ngrok.com/download
2. Extrae el archivo `ngrok.exe` a una carpeta en tu PATH o al proyecto
3. Opcionalmente, crea cuenta gratuita en https://ngrok.com para obtener mejor estabilidad

### Alternativa: Con Chocolatey (Windows):
```powershell
choco install ngrok
```

---

## 📊 Flujo de Ejecución

```
┌─────────────────────────────────────┐
│ Ejecutar start_with_webhook.ps1     │
└────────────┬────────────────────────┘
             │
     ┌───────┴────────┐
     │                │
     ▼                ▼
   ngrok          run.py
(Puerto 5000)   (Flask + Bot)
     │                │
     │ public_url     │
     └────────┬───────┘
              │
        ┌─────▼──────┐
        │  Bot Setup │
        │  Webhook   │
        └─────┬──────┘
              │
        Telegram ──────► Webhook Endpoint
        (Updates)       /telegram/webhook
```

---

## 🔐 Variables de Entorno

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `USE_WEBHOOK` | Activar webhook (true/false) | `true` |
| `NGROK_URL` | URL pública de ngrok | `https://abc123.ngrok.io` |
| `WEBHOOK_SECRET_TOKEN` | Token para validar requests | `token_secreto_123` |

---

## ✨ Características de Seguridad

- ✅ **Token Secreto**: Telegram valida cada request con `X-Telegram-Bot-Api-Secret-Token`
- ✅ **Validación**: El endpoint verifica el token antes de procesar
- ✅ **Fallback Automático**: Si ngrok falla, cambia a polling sin intervención manual

---

## 🐛 Solucionar Problemas

### Error: "ngrok not found"
```
Solución: Instala ngrok desde https://ngrok.com o usa Chocolatey
```

### Error: "Cannot connect to ngrok API"
```
Solución: Verifica que ngrok está ejecutándose en otra terminal
o ejecuta: ngrok http 5000
```

### Webhook no recibe updates
```
Solución: 
1. Verifica que la URL de ngrok es correcta
2. Comprueba en Telegram que el bot está activo
3. Revisa los logs para errores
```

### Cambiar a polling si necesitas
```
Simplemente ejecuta:
cd pizzeria_backend
$env:USE_WEBHOOK = "false"
python run.py
```

---

## 📈 Próximos Pasos (Opcional)

Para producción sin ngrok:
1. Obtén un dominio (ej: tudominio.com)
2. Usa un servicio como Render, Railway o Heroku
3. Configura HTTPS/SSL
4. Usa tu dominio en lugar de ngrok

```python
# En config.py para producción:
WEBHOOK_URL = "https://tudominio.com"
```

---

## 📝 Notas

- **ngrok es temporal**: La URL cambia cada vez que reinicies (excepto con cuenta premium)
- **Conversión automática**: El bot detecta si ngrok está disponible y elige el mejor método
- **Sin cambios en bot handlers**: Los comandos `/start` y `/mispedidos` siguen funcionando igual

¡Listo! 🎉 Ahora tu bot usa webhook cuando sea posible, con fallback a polling automático.
