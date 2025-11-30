import requests
import time
import math

# Configuración
BASE_URL = "http://localhost:5000"  # O tu URL de Railway
DRIVER_ID = "D1"
ORDER_ID = "ORD-123" # Asegúrate de que este pedido exista y esté "En camino"

# Coordenadas (Santa Cruz - Plaza 24 a un punto cercano)
START_LAT = -17.7833
START_LON = -63.1821
END_LAT = -17.7860
END_LON = -63.1850

STEPS = 20
DELAY = 2 # Segundos entre actualizaciones

def update_location(lat, lon):
    url = f"{BASE_URL}/driver/location"
    payload = {
        "driver_id": DRIVER_ID,
        "latitude": lat,
        "longitude": lon
    }
    try:
        requests.post(url, json=payload)
        print(f"📍 Driver en: {lat:.5f}, {lon:.5f}")
    except Exception as e:
        print(f"Error: {e}")

def simulate_route():
    print(f"🚀 Iniciando simulación de ruta para Driver {DRIVER_ID}...")
    
    # 1. Asegurar estado "En camino"
    requests.post(f"{BASE_URL}/driver/pickup", json={"order_id": ORDER_ID})
    print("✅ Estado actualizado a 'En camino'")

    # 2. Moverse
    for i in range(STEPS + 1):
        t = i / STEPS
        # Interpolación lineal simple
        current_lat = START_LAT + (END_LAT - START_LAT) * t
        current_lon = START_LON + (END_LON - START_LON) * t
        
        update_location(current_lat, current_lon)
        time.sleep(DELAY)

    # 3. Entregar
    requests.post(f"{BASE_URL}/driver/deliver", json={"order_id": ORDER_ID})
    print("🎉 Pedido entregado. Fin de simulación.")

if __name__ == "__main__":
    simulate_route()
