# app/routes.py
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

# ... (resto de endpoints)



@app.route('/submit_order', methods=['POST'])
async def submit_order():
    """
    Este endpoint recibe el pedido desde la WebApp (Netlify) y lo guarda en Firestore.
    """
    try:
        data = request.get_json()
        
        if not data or not isinstance(data, dict):
            logger.warning("Request recibida sin un JSON body válido.")
            return jsonify({"status": "error", "message": "Request debe contener un JSON válido."}), 400
            
        chat_id = data.get('chat_id')
        order = data.get('order')

        if not chat_id or not order:
            logger.warning("Pedido recibido sin chat_id u order")
            return jsonify({"status": "error", "message": "Faltan datos (chat_id u order)."}), 400
        
        order['chat_id'] = chat_id 

        logger.info(f"Nuevo pedido recibido del chat_id: {chat_id}")

        # 1. Guardar en la Base de Datos
        exito_db = guardar_pedido_en_firestore(order)
        if not exito_db:
            return jsonify({"status": "error", "message": "Error al guardar en la base de datos (Firebase no conectó)"}), 500
        
        # 2. Notificar al Cliente con la Factura detallada
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

        # 4. Iniciar Simulación de Estados (DEMO)
        # Esto cambiará el estado automáticamente cada X segundos
        simulation_thread = threading.Thread(target=run_order_simulation, args=(order.get('id'),))
        simulation_thread.daemon = True # Para que no bloquee el cierre del server
        simulation_thread.start()

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