import os

# --- CONFIGURACIÓN -- -
BOT_TOKEN = "8334575884:AAEivWr_jKwAQ3qAC2aSc569OJeyY0MCom4"
# Tu URL de Netlify (SIN la barra al final)
WEB_APP_URL = "https://pizzerinanova.netlify.app"
IMAGE_URL = "https://i.postimg.cc/vmTx9Lsc/Gemini-Generated-Image-msl551msl551msl5.png"

# --- ID del Restaurante/Tienda ---
# IMPORTANTE: Debes obtener el chat_id del chat de tu restaurante
# Puedes usar un bot como @userinfobot para obtener este ID
RESTAURANT_CHAT_ID = "1463499995"  # Ejemplo: "123456789"

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


