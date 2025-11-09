# -*- coding: utf-8 -*-
import threading
import asyncio
import uvicorn
import logging
from telegram.ext import Application

from app import app
from app.bot import get_bot_handlers
from config import BOT_TOKEN
from asgiref.wsgi import WsgiToAsgi

logger = logging.getLogger(__name__)

def run_flask():
    """Corre el servidor web Flask usando Uvicorn (compatible con async)"""
    logger.info("Iniciando servidor Flask (Uvicorn) en http://0.0.0.0:5000")
    asgi_app = WsgiToAsgi(app)
    config = uvicorn.Config(asgi_app, host="0.0.0.0", port=5000, log_level="info")
    server = uvicorn.Server(config)
    server.run()

async def run_telegram_bot():
    """Configura y corre el bot de Telegram en modo polling"""
    # Asignamos el loop de asyncio a la app de Flask para que las rutas puedan usarlo
    app.bot_loop = asyncio.get_running_loop()

    application = Application.builder().token(BOT_TOKEN).build()
    
    handlers = get_bot_handlers()
    for handler in handlers:
        application.add_handler(handler)

    logger.info("Iniciando bot de Telegram (polling)...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Mantener este hilo vivo
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logger.info("Iniciando la aplicación...")

    # Iniciar Flask en un hilo separado
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Iniciar el bot de Telegram en el hilo principal
    try:
        asyncio.run(run_telegram_bot())
    except KeyboardInterrupt:
        logger.info("Cerrando la aplicación...")