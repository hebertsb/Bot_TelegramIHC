import os

# --- CONFIGURACIÓN -- -
BOT_TOKEN = "8334575884:AAEivWr_jKwAQ3qAC2aSc569OJeyY0MCom4"
# Tu URL de Netlify (SIN la barra al final)
WEB_APP_URL = "https://pizzerianova1.netlify.app"
IMAGE_URL = "https://i.postimg.cc/vmTx9Lsc/Gemini-Generated-Image-msl551msl551msl5.png"

# --- ID del Restaurante/Tienda ---
# IMPORTANTE: Debes obtener el chat_id del chat de tu restaurante
# Puedes usar un bot como @userinfobot para obtener este ID
RESTAURANT_CHAT_ID = "1463499995"  # Ejemplo: "123456789"

# --- FIREBASE ---

# Construye la ruta absoluta al archivo de credenciales de Firebase

# Se asume que el JSON está en la raíz de la carpeta 'pizzeria_backend'

import base64
import json

# ... (otras configuraciones)

_project_root = os.path.dirname(os.path.abspath(__file__))

# Lógica para cargar credenciales de Firebase
# 1. Intentar cargar desde variable de entorno (Producción/Railway)
firebase_base64 = os.environ.get("FIREBASE_CREDENTIALS_BASE64")

if firebase_base64:
    try:
        # Decodificar base64 a string y luego a JSON
        decoded_json = base64.b64decode(firebase_base64).decode('utf-8')
        FIREBASE_CREDENTIALS = json.loads(decoded_json)
        print("✅ Credenciales de Firebase cargadas desde variable de entorno.")
    except Exception as e:
        print(f"❌ Error al decodificar credenciales de entorno: {e}")
        FIREBASE_CREDENTIALS = None
else:
    # 2. Fallback a archivo local (Desarrollo)
    FIREBASE_CREDENTIALS = os.path.join(_project_root, "pizzeriabackend-firebase-adminsdk-fbsvc-f65e1c0eb7.json")
    print(f"ℹ️ Usando archivo local de credenciales: {FIREBASE_CREDENTIALS}")



# --- GEMINI API KEY ---

# ¡¡¡IMPORTANTE!!! No dejes esta clave visible en el código en un repositorio público.

# Para producción, es MUY recomendable cargarla desde una variable de entorno.

# Ejemplo: GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

GEMINI_API_KEY = "AIzaSyBmH9IhaxwGfb80GzuOXJmHWESeAqO1aUY"


