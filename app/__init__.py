import logging
from flask import Flask
from flask_cors import CORS

# Configura el logging principal
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# --- INICIALIZACIÓN DE SERVICIOS ---
# La inicialización de Firebase ocurre automáticamente cuando el módulo `services` es importado por primera vez.
# No es necesario llamarlo explícitamente aquí.
# -----------------------------------


# 1. Crear la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir peticiones desde tu frontend