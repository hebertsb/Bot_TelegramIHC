import os
import base64
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (si existe, para desarrollo local)
load_dotenv()

# --- CONFIGURACIÓN ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEB_APP_URL = os.environ.get("WEB_APP_URL")
IMAGE_URL = "https://i.postimg.cc/vmTx9Lsc/Gemini-Generated-Image-msl551msl551msl5.png"

# --- WEBHOOK CONFIG ---
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") # URL pública (ej. Railway o ngrok)
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_SECRET_TOKEN = os.environ.get("WEBHOOK_SECRET_TOKEN", "my-secret-token")

# --- ID del Restaurante/Tienda ---
RESTAURANT_CHAT_ID = os.environ.get("RESTAURANT_CHAT_ID")

# --- FIREBASE ---
_project_root = os.path.dirname(os.path.abspath(__file__))

# Lógica para cargar credenciales de Firebase
# 1. Intentar cargar desde variable de entorno (Producción/Railway/Local .env)
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
    # 2. Fallback a archivo local (Solo si NO existe la variable de entorno)
    local_path = os.path.join(_project_root, "pizzerianova-firebase-adminsdk-fbsvc-5bea994d7b.json")
    if os.path.exists(local_path):
        FIREBASE_CREDENTIALS = local_path
        print(f"ℹ️ Usando archivo local de credenciales: {FIREBASE_CREDENTIALS}")
    else:
        print("⚠️ NO se encontraron credenciales de Firebase (ni variable de entorno ni archivo local).")
        FIREBASE_CREDENTIALS = None

# --- GEMINI API KEY ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")



# --- UBICACIÓN DEL RESTAURANTE ---
# Coordenadas fijas para que Frontend y Driver App consuman la misma fuente de verdad.
RESTAURANT_LOCATION = {
  "latitude": -17.7832662,
  "longitude": -63.1820985,
  "name": "Pizzería Nova"
}

# Versión desplazada para visualización en mapa (evita superposición exacta)
RESTAURANT_MAP_LOCATION = {
  "latitude": RESTAURANT_LOCATION["latitude"] - 0.00035,
  "longitude": RESTAURANT_LOCATION["longitude"] + 0.0006
}
