import os
from pathlib import Path

# Cargar variables de entorno si existe archivo .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

# --- CONFIGURACIÓN -- -
BOT_TOKEN = "8334575884:AAEivWr_jKwAQ3qAC2aSc569OJeyY0MCom4"
# Tu URL de Netlify (SIN la barra al final)
WEB_APP_URL = "https://pizzerianova.netlify.app/"
IMAGE_URL = "https://i.postimg.cc/vmTx9Lsc/Gemini-Generated-Image-msl551msl551msl5.png"

# --- WEBHOOK TELEGRAM ---
# URL pública donde Telegram enviará los updates
# Opciones:
#   1. Con ngrok: se configura dinámicamente en run.py
#   2. Dominio personalizado: https://tu-dominio.com (para producción)
#   3. Localhost: http://localhost:5000 (solo desarrollo)
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://localhost:5000")
# Ruta donde recibiremos los updates
WEBHOOK_PATH = "/telegram/webhook"
# Token secreto para validar que las requests vienen de Telegram
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN", "tu_token_secreto_aqui_123456")

# --- ID del Restaurante/Tienda ---
# IMPORTANTE: Debes obtener el chat_id del chat de tu restaurante
# Puedes usar un bot como @userinfobot para obtener este ID
RESTAURANT_CHAT_ID = "6286120094"  # Ejemplo: "123456789"

# --- FIREBASE ---

# Construye la ruta absoluta al archivo de credenciales de Firebase

# Se asume que el JSON está en la raíz de la carpeta 'pizzeria_backend'

_project_root = os.path.dirname(os.path.abspath(__file__))

FIREBASE_KEY_PATH = os.path.join(_project_root, "pizzeriabackend-firebase-adminsdk-fbsvc-f65e1c0eb7.json")



# --- GEMINI API KEY ---

# ¡¡¡IMPORTANTE!!! No dejes esta clave visible en el código en un repositorio público.

# Para producción, es MUY recomendable cargarla desde una variable de entorno.

# Ejemplo: GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_API_KEY = "AIzaSyBmH9IhaxwGfb80GzuOXJmHWESeAqO1aUY"


