# -*- coding: utf-8 -*-
import threading
import asyncio
import uvicorn
import logging
import os
import subprocess
import time
import platform
from telegram.ext import Application

from app import app
from app.bot import get_bot_handlers
from app.routes import telegram_service
from config import BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBHOOK_SECRET_TOKEN
from asgiref.wsgi import WsgiToAsgi
import os

logger = logging.getLogger(__name__)

def get_ngrok_url():
    """
    Obtiene la URL de ngrok. 
    Intenta conectarse al API local de ngrok (puerto 4040)
    """
    try:
        import requests
        response = requests.get("http://localhost:4040/api/tunnels")
        data = response.json()
        if data['tunnels']:
            ngrok_url = data['tunnels'][0]['public_url']
            return ngrok_url
    except Exception as e:
        logger.warning(f"No se pudo obtener URL de ngrok: {e}")
    return None

def start_ngrok():
    """
    Inicia ngrok automáticamente en el puerto 5000
    Debes tener ngrok instalado y en PATH
    """
    try:
        system = platform.system()
        if system == "Windows":
            # En Windows, intenta ejecutar ngrok en background
            subprocess.Popen(["ngrok", "http", "5000"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        else:
            # En Linux/Mac
            subprocess.Popen(["ngrok", "http", "5000"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        
        # Esperar a que ngrok se inicie
        logger.info("Esperando a que ngrok se inicie...")
        time.sleep(3)
        
        ngrok_url = get_ngrok_url()
        if ngrok_url:
            logger.info(f"✅ ngrok iniciado: {ngrok_url}")
            return ngrok_url
        else:
            logger.warning("⚠️ ngrok no pudo ser iniciado automáticamente")
            logger.warning("Inicia ngrok manualmente con: ngrok http 5000")
            return None
    except FileNotFoundError:
        logger.error("❌ ngrok no encontrado. Instálalo desde https://ngrok.com")
        return None
    except Exception as e:
        logger.error(f"Error al iniciar ngrok: {e}")
        return None

def run_flask():
    """Corre el servidor web Flask usando Uvicorn (compatible con async)"""
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Iniciando servidor Flask (Uvicorn) en http://0.0.0.0:{port}")
    asgi_app = WsgiToAsgi(app)
    config = uvicorn.Config(asgi_app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    server.run()

async def run_telegram_bot_webhook(webhook_url):
    """
    Configura y corre el bot de Telegram en modo WEBHOOK
    """
    # Asignamos el loop de asyncio a la app de Flask para que las rutas puedan usarlo
    app.bot_loop = asyncio.get_running_loop() # type: ignore

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN no está configurado")

    application = Application.builder().token(BOT_TOKEN).build()
    
    # Configurar el servicio de Telegram
    telegram_service.bot = application.bot
    telegram_service.loop = asyncio.get_running_loop()
    telegram_service.application = application # type: ignore
    
    handlers = get_bot_handlers()
    for handler in handlers:
        application.add_handler(handler)

    logger.info("Iniciando bot de Telegram (WEBHOOK)...")
    await application.initialize()
    await application.start()
    
    # Construir la URL completa del webhook
    full_webhook_url = f"{webhook_url}{WEBHOOK_PATH}"
    
    logger.info(f"Configurando webhook en: {full_webhook_url}")
    
    try:
        # Establecer el webhook
        await application.bot.set_webhook(
            url=full_webhook_url,
            secret_token=WEBHOOK_SECRET_TOKEN,
            drop_pending_updates=True
        )
        logger.info("✅ Webhook configurado exitosamente")
        
        # Verificar que el webhook está configurado
        webhook_info = await application.bot.get_webhook_info()
        logger.info(f"Webhook info: {webhook_info}")
        
    except Exception as e:
        logger.error(f"Error al configurar webhook: {e}")
        raise

    # Mantener este hilo vivo
    while True:
        await asyncio.sleep(3600)

async def run_telegram_bot_polling():
    """
    Configura y corre el bot de Telegram en modo POLLING (fallback)
    """
    # Asignamos el loop de asyncio a la app de Flask para que las rutas puedan usarlo
    app.bot_loop = asyncio.get_running_loop() # type: ignore

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN no está configurado")

    application = Application.builder().token(BOT_TOKEN).build()
    
    # Configurar el servicio de Telegram
    telegram_service.bot = application.bot
    telegram_service.loop = asyncio.get_running_loop()
    telegram_service.application = application # type: ignore
    
    handlers = get_bot_handlers()
    for handler in handlers:
        application.add_handler(handler)

    logger.info("Iniciando bot de Telegram (POLLING - modo fallback)...")
    await application.initialize()
    await application.start()
    
    # Configurar los comandos del bot ANTES de iniciar polling
    try:
        from telegram import BotCommand
        commands = [
            BotCommand("start", "Iniciar el bot"),
            BotCommand("menu", "Abrir el menú del restaurante"),
            BotCommand("mispedidos", "Ver el estado de mis pedidos"),
            BotCommand("help", "Obtener ayuda")
        ]
        await application.bot.set_my_commands(commands)
        logger.info("✅ Comandos del bot configurados exitosamente")
    except Exception as e:
        logger.error(f"❌ Error al configurar comandos del bot: {e}")
    
    # Ahora sí, iniciar el polling
    if application.updater:
        await application.updater.start_polling()
    logger.info("Bot escuchando mensajes...")

    # Mantener este hilo vivo
    while True:
        await asyncio.sleep(3600)
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logger.info("Iniciando la aplicación...")

    # Iniciar Flask en un hilo separado
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Determinar si usar webhook o polling
    # En Railway, WEBHOOK_URL debe estar definida.
    webhook_url_env = os.environ.get("WEBHOOK_URL")
    
    try:
        if webhook_url_env:
            # MODO PRODUCCIÓN (Railway)
            logger.info(f"🚀 Modo WEBHOOK activado (Producción). URL: {webhook_url_env}")
            # Eliminar trailing slash si existe
            webhook_url_env = webhook_url_env.rstrip('/')
            asyncio.run(run_telegram_bot_webhook(webhook_url_env))
            
        else:
            # MODO DESARROLLO LOCAL (ngrok o Polling)
            use_webhook = os.environ.get("USE_WEBHOOK", "true").lower() == "true"
            
            if use_webhook:
                logger.info("🚀 Modo WEBHOOK activado (Local/ngrok)")
                # Intentar iniciar ngrok automáticamente
                ngrok_url = start_ngrok()
                
                if ngrok_url:
                    ngrok_url = ngrok_url.rstrip('/')
                    logger.info(f"Usando webhook URL: {ngrok_url}")
                    asyncio.run(run_telegram_bot_webhook(ngrok_url))
                else:
                    logger.warning("No se pudo obtener URL de ngrok. Cambiando a POLLING...")
                    asyncio.run(run_telegram_bot_polling())
            else:
                logger.info("📡 Modo POLLING activado")
                asyncio.run(run_telegram_bot_polling())
            
    except KeyboardInterrupt:
        logger.info("Cerrando la aplicación...")
