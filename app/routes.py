import logging
import asyncio
import json
import httpx
import google.generativeai as genai
from flask import request, jsonify, render_template_string
from datetime import datetime
import pytz
import threading
import time
import math
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Importaciones de tu aplicación
from app import app
from config import RESTAURANT_CHAT_ID, GEMINI_API_KEY
from app.services import guardar_pedido_en_firestore, obtener_pedido_por_id, actualizar_estado_pedido, obtener_todos_los_pedidos
from app.menu_data import products

logger = logging.getLogger(__name__)

# --- Configuración de la API de Gemini ---
genai.configure(api_key=GEMINI_API_KEY)

class TelegramService:
    """Servicio para encapsular la lógica de envío de mensajes de Telegram."""
    def __init__(self):
        self.bot = None
        self.loop = None

    def configure(self, bot, loop):
        """Configura el bot y el loop de eventos después de la inicialización."""
        self.bot = bot
        self.loop = loop
        logger.info("El servicio de Telegram ha sido configurado exitosamente.")

    def send_message(self, chat_id, text, parse_mode='HTML', reply_markup=None):
        """Envía un mensaje de forma segura en el loop de eventos del bot."""
        if not self.loop or not self.bot:
            logger.warning("El bot o el loop de eventos no están disponibles. No se puede enviar el mensaje.")
            return

        coro = self.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup
        )
        asyncio.run_coroutine_threadsafe(coro, self.loop)

# --- Instancia del Servicio de Telegram ---
# Se crea una instancia vacía que será configurada en run.py
telegram_service = TelegramService()

def generate_telegram_invoice_text(order):
    """Genera el texto de la factura para ser enviado por Telegram."""
    currency = order.get('currency', 'Bs')
    
    items_list = []
    for item in order.get('items', []):
        item_total = item['price'] * item['quantity']
        # Usamos formato de ancho fijo simple con `ljust` para alinear
        name_part = f"{item.get('emoji', '🍕')} {item['name']}"
        price_part = f"x{item['quantity']} ... {currency} {item_total:.2f}"
        items_list.append(f"<code>{name_part.ljust(20)} {price_part}</code>")
    
    items_text = "\n".join(items_list)
    
    address_text = order.get('address', 'No especificada')
    if not address_text and order.get('location'):
        location = order['location']
        address_text = f"Lat: {location.get('latitude')}, Lon: {location.get('longitude')}"

    # Formatear fecha con zona horaria de Bolivia
    date_ts = order.get('date_ts')
    date_str = order.get('date')
    
    try:
        if isinstance(date_ts, (int, float)):
             # Si viene timestamp en ms
            dt_utc = datetime.fromtimestamp(date_ts / 1000, tz=pytz.utc)
        elif date_str:
             # Si viene string ISO
            dt_utc = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt_utc = datetime.now(pytz.utc)

        # Convertir a America/La_Paz
        bolivia_tz = pytz.timezone('America/La_Paz')
        dt_local = dt_utc.astimezone(bolivia_tz)
        date_formatted = dt_local.strftime("%d/%m/%Y %H:%M")
    except Exception as e:
        logger.error(f"Error formateando fecha: {e}")
        date_formatted = "Fecha desconocida"

    # Datos del Cliente
    customer_name = order.get('customer_name', 'Cliente')
    customer_nit = order.get('customer_nit', 'S/N')
    customer_phone = order.get('customer_phone', 'No registrado')

    invoice_text = (
        f"<b>🍕 Pizzeria Nova - Factura 🍕</b>\n\n"
        f"¡Gracias por tu pedido! Lo hemos recibido y ya está en marcha.\n\n"
        f"<b>Factura N°:</b> <code>{order.get('id')}</code>\n"
        f"<b>Fecha:</b> {date_formatted}\n"
        f"<b>Estado:</b> {order.get('status', 'Confirmado')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>DATOS DEL CLIENTE:</b>\n"
        f"<b>Nombre:</b> {customer_name}\n"
        f"<b>NIT/CI:</b> {customer_nit}\n"
        f"<b>Teléfono:</b> {customer_phone}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>DETALLES DEL PEDIDO:</b>\n"
        f"{items_text}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Total a Pagar: {currency} {order.get('total', 0):.2f}</b>\n\n"
        f"<b>Dirección de Entrega:</b>\n"
        f"<i>{address_text}</i>\n\n"
        f"<b>Método de Pago:</b> {order.get('paymentMethod')}\n\n"
        f"Te mantendremos informado sobre el estado de tu pedido."
    )
    return invoice_text


# Función auxiliar para generar el HTML de la factura (para reutilizar)
def generate_invoice_html(order):
    """Genera una factura simple en HTML"""
    currency = order.get('currency', 'Bs')
    
    # Función para formatear ítems de la factura
    items_html = ""
    for item in order.get('items', []):
        total_item = item['price'] * item['quantity']
        items_html += f"""
        <tr>
            <td style="text-align: left; padding: 8px 0;">{item['name']} ({item.get('emoji', '🍕')})</td>
            <td style="text-align: center;">{item['quantity']}</td>
            <td style="text-align: right;">{currency} {item['price']:.2f}</td>
            <td style="text-align: right;">{currency} {total_item:.2f}</td>
        </tr>
        """

    # Formatear fecha con zona horaria de Bolivia
    date_ts = order.get('date_ts')
    date_str = order.get('date')
    
    try:
        if isinstance(date_ts, (int, float)):
             # Si viene timestamp en ms
            dt_utc = datetime.fromtimestamp(date_ts / 1000, tz=pytz.utc)
        elif date_str:
             # Si viene string ISO
            dt_utc = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            dt_utc = datetime.now(pytz.utc)

        # Convertir a America/La_Paz
        bolivia_tz = pytz.timezone('America/La_Paz')
        dt_local = dt_utc.astimezone(bolivia_tz)
        invoice_date = dt_local.strftime("%d/%m/%Y %H:%M:%S")
    except Exception as e:
        logger.error(f"Error formateando fecha HTML: {e}")
        invoice_date = "Fecha desconocida"

    # Datos del Cliente
    customer_name = order.get('customer_name', 'Cliente')
    customer_nit = order.get('customer_nit', 'S/N')
    customer_phone = order.get('customer_phone', 'No registrado')

    # Estilo de la factura (se recomienda usar estilos inline para PDFs)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Factura Pizzeria Nova #{order['id']}</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            .container {{ max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #E94E1B; text-align: center; border-bottom: 2px solid #ddd; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border-bottom: 1px solid #eee; padding: 8px; }}
            th {{ background-color: #f5f5f5; text-align: left; }}
            .summary-table td {{ border: none; font-weight: bold; }}
            .total-row td {{ border-top: 2px solid #333; font-size: 1.2em; }}
            .client-info {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🍕 Factura Pizzeria Nova</h1>
            
            <div class="client-info">
                <p><strong>Factura N°:</strong> {order['id']}</p>
                <p><strong>Fecha/Hora:</strong> {invoice_date}</p>
                <p><strong>Cliente:</strong> {customer_name}</p>
                <p><strong>NIT/CI:</strong> {customer_nit}</p>
                <p><strong>Teléfono:</strong> {customer_phone}</p>
            </div>

            <p><strong>Dirección de Entrega:</strong> {order.get('address', 'No especificada')}</p>
            <p><strong>Método de Pago:</strong> {order['paymentMethod']}</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th style="text-align: center;">Cant.</th>
                        <th style="text-align: right;">Precio Unit.</th>
                        <th style="text-align: right;">Total Item</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>

            <table class="summary-table" style="margin-top: 20px; float: right; width: 50%;">
                <tr class="total-row">
                    <td>Total a Pagar:</td>
                    <td style="text-align: right;">{currency} {order.get('total', 0):.2f}</td>
                </tr>
            </table>
            <div style="clear: both;"></div>
            
            <p style="text-align: center; margin-top: 30px; font-size: 0.8em; color: #777;">
                Gracias por tu pedido. Este documento es un comprobante de venta simplificado.
            </p>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/')
def index():
    return "¡El servidor Backend de Pizzería está funcionando!"

@app.route('/get_products', methods=['GET'])
def get_products():
    """
    Endpoint para obtener la lista completa de productos del menú.
    """
    return jsonify(products)

@app.route('/factura/<string:order_id>', methods=['GET'])
def get_invoice(order_id):
    """
    Ruta para ver la factura de un pedido específico.
    """
    try:
        # 1. Obtener el pedido de Firestore
        order = obtener_pedido_por_id(order_id)
        
        if not order:
            return f"Error 404: Pedido #{order_id} no encontrado.", 404

        # 2. Generar y devolver el HTML
        html_content = generate_invoice_html(order)
        return render_template_string(html_content)

    except Exception as e:
        logger.error(f"Error al generar factura para {order_id}: {e}", exc_info=True)
        return "Error interno del servidor al procesar la factura.", 500

def process_order_status_update(order_id, nuevo_estado, driver_location=None):
    """
    Lógica central para actualizar el estado y notificar.
    Retorna True si tuvo éxito, False si falló.
    """
    try:
        # 1. Obtener el pedido
        order = obtener_pedido_por_id(order_id)
        if not order:
            logger.warning(f"Intento de actualizar pedido inexistente: {order_id}")
            return False

        # 2. Actualizar en BD
        if not actualizar_estado_pedido(order_id, nuevo_estado, driver_location):
            return False
        
        # 3. Notificar al cliente
        
        # Dividimos el viaje en pasos de actualización (ej. cada 3 segundos reales)
        UPDATE_INTERVAL_REAL = 3.0 
        steps = int(wait_travel / UPDATE_INTERVAL_REAL)
        if steps < 1: steps = 1
        
        for i in range(1, steps + 1):
            time.sleep(UPDATE_INTERVAL_REAL)
            # Interpolación Lineal
            fraction = i / steps
            current_lat = RESTAURANT_LAT + (client_lat - RESTAURANT_LAT) * fraction
            current_lon = RESTAURANT_LON + (client_lon - RESTAURANT_LON) * fraction
            
            process_order_status_update(order_id, "En camino", driver_location={"latitude": current_lat, "longitude": current_lon})
            logger.info(f"Simulación {order_id}: Driver en {current_lat:.5f}, {current_lon:.5f}")

        # Paso 5: Entregado
        process_order_status_update(order_id, "Entregado", driver_location={"latitude": client_lat, "longitude": client_lon})

    except Exception as e:
        logger.error(f"Error en simulación del pedido {order_id}: {e}", exc_info=True)

@app.route('/update_status/<string:order_id>', methods=['POST'])
def update_order_status(order_id):
    """
    Endpoint para que un sistema externo (ej. un panel de admin) actualice el estado de un pedido.
    """
    try:
        # Intentar obtener JSON de forma estándar
        data = None
        try:
            data = request.get_json()
        except Exception:
            pass

        # Si falla (por encoding), intentamos decodificar manualmente
        if data is None:
            raw_data = request.get_data()
            try:
                # Intento 1: UTF-8
                decoded_str = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                # Intento 2: Latin-1 (común en Windows/PowerShell)
                logger.warning(f"Fallo decodificación UTF-8 para {order_id}, intentando latin-1")
                decoded_str = raw_data.decode('latin-1')
            
            data = json.loads(decoded_str)

        logger.info(f"Recibida petición de actualización para {order_id}. Payload: {data}")
        
        nuevo_estado = data.get('status')
        driver_location = data.get('driver_location') # Opcional

        if not nuevo_estado:
            return jsonify({"status": "error", "message": "El campo 'status' es requerido."}), 400

        if process_order_status_update(order_id, nuevo_estado, driver_location):
             return jsonify({"status": "success", "order_id": order_id, "new_status": nuevo_estado})
        else:
             # Si falla process_order_status_update, es porque falló la BD o no existe el pedido.
             # La notificación fallida YA está manejada dentro y no retorna False.
             return jsonify({"status": "error", "message": "No se pudo actualizar el pedido (Error BD o ID inválido)."}), 500

    except Exception as e:
        logger.error(f"Error NO CONTROLADO en /update_status/{order_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Error interno del servidor."}), 500


@app.route('/get_orders', methods=['GET'])
def get_orders():
    """
    Endpoint para obtener todos los pedidos, diseñado para el panel de administración.
    """
    try:
        pedidos = obtener_todos_los_pedidos()
        return jsonify(pedidos)
    except Exception as e:
        logger.error(f"Error en /get_orders: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Error interno del servidor al obtener los pedidos."}), 500

@app.route('/get_order/<string:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Endpoint para obtener un pedido específico por su ID.
    Útil para el seguimiento del pedido por parte del cliente.
    """
    try:
        order = obtener_pedido_por_id(order_id)
        if not order:
            return jsonify({"status": "error", "message": "Pedido no encontrado"}), 404
        return jsonify(order)
    except Exception as e:
        logger.error(f"Error en /get_order/{order_id}: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Error interno del servidor."}), 500

@app.route('/submit_order', methods=['POST'])
def submit_order():
    """
    Este endpoint recibe el pedido desde la WebApp (Netlify) y lo guarda en Firestore.
    """
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("Request recibida sin body o con body vacío.")
            return jsonify({"status": "error", "message": "Request debe contener un JSON válido."}), 400
            
        if not isinstance(data, dict):
             logger.warning(f"Request body no es un dict: {type(data)}")
             return jsonify({"status": "error", "message": "El cuerpo debe ser un objeto JSON."}), 400

        chat_id = data.get('chat_id')
        order = data.get('order')

        if not chat_id or not order:
            logger.warning("Pedido recibido sin chat_id u order")
            return jsonify({"status": "error", "message": "Faltan datos (chat_id u order)."}), 400
        
        if not isinstance(order, dict):
            logger.warning(f"El campo 'order' no es un dict: {type(order)}")
            return jsonify({"status": "error", "message": "El campo 'order' debe ser un objeto JSON."}), 400


        order['chat_id'] = chat_id

        # Validar y procesar ubicación
        location = order.get('location')
        if location:
            # Si la ubicación viene como string, intenta convertirla a dict
            if isinstance(location, str):
                try:
                    location = json.loads(location)
                    order['location'] = location
                except Exception as e:
                    logger.warning(f"No se pudo convertir location a dict: {location} - {e}")
            # Si la ubicación es dict, verifica que tenga lat/lng
            if isinstance(location, dict):
                lat = location.get('lat')
                lng = location.get('lng')
                if lat is None or lng is None:
                    logger.warning(f"Ubicación incompleta: {location}")
            else:
                logger.warning(f"Formato de ubicación no reconocido: {location}")
        else:
            logger.info("Pedido recibido sin ubicación (location)")

        # Generar ID si no existe (Robustez)
        if 'id' not in order:
            import random
            random_suffix = random.randint(1000, 9999)
            generated_id = f"ORD-{int(time.time())}-{random_suffix}"
            order['id'] = generated_id
            logger.warning(f"Pedido recibido sin ID. Se generó uno automático: {generated_id}")

        logger.info(f"Nuevo pedido recibido del chat_id: {chat_id}")
        logger.info(f"Datos del pedido a guardar: {order}")

        # 1. Guardar en la Base de Datos
        try:
            exito_db = guardar_pedido_en_firestore(order)
            if not exito_db:
                logger.error("guardar_pedido_en_firestore devolvió False")
                return jsonify({"status": "error", "message": "Error al guardar en la base de datos (Firebase no conectó)"}), 500
        except Exception as e_db:
            logger.error(f"Excepción al llamar guardar_pedido_en_firestore: {e_db}", exc_info=True)
            return jsonify({"status": "error", "message": "Excepción al guardar en BD."}), 500
        
        # 2. Notificar al Cliente con la Factura detallada
        try:
            if chat_id == "LOCAL_TEST":
                logger.info(f"Omitiendo notificación Telegram para chat_id de prueba: {chat_id}")
            else:
                invoice_text = generate_telegram_invoice_text(order)
                invoice_url = f"{request.host_url}factura/{order.get('id')}"
                
                keyboard = [[
                    InlineKeyboardButton("Ver Factura Web 🧾", url=invoice_url)
                ]]
                reply_markup = InlineKeyboardMarkup(keyboard)

                # Usamos el servicio para notificar al cliente
                telegram_service.send_message(
                    chat_id=chat_id, 
                    text=invoice_text, 
                    reply_markup=reply_markup
                )
                
                # 3. Notificar al Restaurante (Alerta)
                # Usamos Bs en lugar de $
                items_summary = "\n".join([f"  - {item['name']} (x{item['quantity']}) - Bs {item['price'] * item['quantity']:.2f}" for item in order.get('items', [])])
                address_text = order.get('address', f"Coords: {order.get('location', 'N/A')}")
                
                # Datos del cliente para el restaurante
                customer_name = order.get('customer_name', 'Cliente')
                customer_phone = order.get('customer_phone', 'No registrado')
                
                restaurant_alert = (
                    f"<b>¡NUEVO PEDIDO!</b> - #{order.get('id')}\n"
                    f"<b>Cliente:</b> {customer_name} (ID: {chat_id})\n"
                    f"<b>Teléfono:</b> {customer_phone}\n"
                    f"<b>Total:</b> Bs {order.get('total')}\n"
                    f"<b>Dirección:</b> {address_text}\n"
                    f"<b>Items:</b>\n{items_summary}"
                )
                # Usamos el servicio para notificar al restaurante
                telegram_service.send_message(
                    chat_id=RESTAURANT_CHAT_ID, 
                    text=restaurant_alert
                )
        except Exception as e_notify:
            logger.error(f"Error al enviar notificaciones para pedido {order.get('id')}: {e_notify}", exc_info=True)
            # No retornamos error 500, porque el pedido YA se guardó en la BD.
            # Solo logueamos el error.

        # 4. Iniciar Simulación de Estados (DEMO)
        # Esto cambiará el estado automáticamente cada X segundos
        try:
            simulation_thread = threading.Thread(target=run_order_simulation, args=(order.get('id'),))
            simulation_thread.daemon = True # Para que no bloquee el cierre del server
            simulation_thread.start()
        except Exception as e_sim:
             logger.error(f"Error al iniciar simulación para {order.get('id')}: {e_sim}")

        return jsonify({"status": "success", "order_id": order.get('id')})

    except Exception as e:
        logger.error(f"Error crítico en /submit_order: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Error interno del servidor."}), 500

@app.route('/generate_pizza_idea', methods=['POST'])
def generate_pizza_idea():
    """
    Endpoint para generar una idea de pizza (nombre y descripción) usando Gemini.
    Recibe una lista de ingredientes en el cuerpo de la solicitud.
    """
    try:
        # 1. Obtener los ingredientes del request
        data = request.get_json()
        if not data or 'ingredients' not in data:
            return jsonify({"error": "La lista de 'ingredients' es requerida."}), 400

        ingredients = data['ingredients']
        if not isinstance(ingredients, list) or len(ingredients) == 0:
            return jsonify({"error": "El campo 'ingredients' debe ser una lista no vacía."}), 400

        ingredients_text = ", ".join(ingredients)
        logger.info(f"Generando idea de pizza con ingredientes: {ingredients_text}")

        # 2. Crear el prompt para Gemini
        prompt = (
            f"Eres un chef de pizzas experto y creativo. "
            f"Tu tarea es inventar un nombre y una descripción para una nueva pizza basada en una lista de ingredientes. "
            f"Ingredientes: {ingredients_text}. "
            f"Por favor, responde únicamente con un objeto JSON válido que contenga dos claves: 'name' (el nombre de la pizza) y 'description' (una descripción corta y apetitosa). "
            f"No incluyas ninguna otra palabra, explicación o formato markdown como ```json."
        )

        # 3. Llamar a la API de Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # 4. Procesar la respuesta
        # Limpiar la respuesta para asegurarse de que es un JSON válido
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        idea = json.loads(cleaned_response_text)

        if 'name' not in idea or 'description' not in idea:
                raise ValueError("La respuesta de la IA no contiene 'name' o 'description'.")

        logger.info(f"Idea generada: {idea}")
        return jsonify(idea)

    except json.JSONDecodeError:
        logger.error(f"Error al decodificar la respuesta de Gemini: {response.text}")
        return jsonify({"error": "No se pudo procesar la respuesta del servicio de IA. Inténtalo de nuevo."}), 500
    except Exception as e:
        logger.error(f"Error en /generate_pizza_idea: {e}", exc_info=True)
        return jsonify({"error": "Ocurrió un error inesperado al generar la idea."}), 500

@app.route('/reverse_geocode', methods=['GET'])
async def reverse_geocode():
    """
    Proxy para realizar geocodificación inversa usando Nominatim (OpenStreetMap).
    Esto evita problemas de CORS en el frontend al realizar la petición desde el servidor.
    """
    try:
        lat = request.args.get('lat')
        lon = request.args.get('lon')

        if not lat or not lon:
            return jsonify({"error": "Parámetros 'lat' y 'lon' son requeridos."}), 400

        # Validar que sean números
        try:
            float(lat)
            float(lon)
        except ValueError:
            return jsonify({"error": "Latitud y longitud deben ser números válidos."}), 400

        # URL de Nominatim
        nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        
        # Headers requeridos por Nominatim (User-Agent es obligatorio)
        headers = {
            "User-Agent": "PizzeriaNovaBot/1.0 (hebertsb@gmail.com)" 
        }
        
        params = {
            "format": "json",
            "lat": lat,
            "lon": lon,
            "zoom": 18,
            "addressdetails": 1
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(nominatim_url, params=params, headers=headers, timeout=10.0)
            
            if response.status_code != 200:
                logger.error(f"Error de Nominatim: {response.status_code} - {response.text}")
                return jsonify({"error": "No se pudo obtener la dirección del servicio externo."}), 502
            
            data = response.json()
            
            # Extraer el nombre legible
            display_name = data.get('display_name', 'Dirección desconocida')
            
            return jsonify({
                "display_name": display_name,
                "raw": data # Opcional: devolver datos crudos si el frontend los necesita
            })

    except httpx.RequestError as e:
        logger.error(f"Error de conexión al llamar a Nominatim: {e}", exc_info=True)
        return jsonify({"error": "Error de conexión con el servicio de mapas."}), 503
    except Exception as e:
        logger.error(f"Error inesperado en /reverse_geocode: {e}", exc_info=True)
        return jsonify({"error": "Error interno del servidor."}), 500