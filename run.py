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

import os

# ... imports ...

def run_flask():
    """Corre el servidor web Flask usando Uvicorn (compatible con async)"""
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Iniciando servidor Flask (Uvicorn) en http://0.0.0.0:{port}")
    asgi_app = WsgiToAsgi(app)
    config = uvicorn.Config(asgi_app, host="0.0.0.0", port=port, log_level="info")
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
    await application.updater.start_polling()
    logger.info("Bot escuchando mensajes...")

    # Mantener este hilo vivo
    while True:
        await asyncio.sleep(3600)
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