# -*- coding: utf-8 -*-
import logging
import time
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot, WebAppInfo
from telegram.ext import ContextTypes, CommandHandler

from config import WEB_APP_URL, IMAGE_URL
# Importamos el servicio de Telegram para poder configurarlo
from app.routes import telegram_service

logger = logging.getLogger(__name__)

def setup_telegram_service(bot: Bot, loop: asyncio.AbstractEventLoop):
    """Configura el servicio de Telegram con el bot y el loop de eventos correctos."""
    telegram_service.bot = bot
    telegram_service.loop = loop
    logger.info("El servicio de Telegram ha sido configurado exitosamente.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        logger.warning("La actualización no contiene un mensaje o un usuario.")
        return

    user = update.effective_user
    chat_id = update.message.chat_id
    logger.info(f"Usuario {user.first_name} (ID: {chat_id}) inició el bot.")

    web_app_url_with_user = f"{WEB_APP_URL}?chat_id={chat_id}"

    caption_text = (
        f"<b>Hola, {user.first_name}!</b>\n\n"
        "<i>Donde cada pizza es una obra de arte.</i>\n\n"
        "Explora nuestro menu, crea tu propia pizza "
        "o pide tus favoritas. Todo a un toque de distancia!"
    )

    keyboard = [[
        InlineKeyboardButton(
            "Hacer Mi Pedido 🍕",
            web_app=WebAppInfo(url=f"{web_app_url_with_user}&v={int(time.time())}")
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await update.message.reply_photo(
            photo=IMAGE_URL,
            caption=caption_text,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error al enviar la foto: {e}.")
        await update.message.reply_html(caption_text, reply_markup=reply_markup)


async def mis_pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        logger.warning("La actualización no contiene un mensaje.")
        return
        
    chat_id = update.message.chat_id
    url_con_hash = f"{WEB_APP_URL}?chat_id={chat_id}#mis-pedidos"

    keyboard = [[
        InlineKeyboardButton(
            "Ver mis Pedidos 🛒",
            web_app=WebAppInfo(url=f"{url_con_hash}&v={int(time.time())}")
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        "Toca el boton para ver el estado de tus pedidos:",
        reply_markup=reply_markup
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /menu - Abre el menú del restaurante"""
    if not update.message:
        logger.warning("La actualización no contiene un mensaje.")
        return
        
    chat_id = update.message.chat_id
    web_app_url_with_user = f"{WEB_APP_URL}?chat_id={chat_id}"

    keyboard = [[
        InlineKeyboardButton(
            "Abrir Menú del Restaurante 🍕",
            web_app=WebAppInfo(url=f"{web_app_url_with_user}&v={int(time.time())}")
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        "📋 <b>Menú de Pizzería Nova</b>\n\n"
        "Explora nuestro delicioso menú con pizzas, bebidas, postres y más!",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help - Muestra ayuda sobre los comandos disponibles"""
    if not update.message:
        logger.warning("La actualización no contiene un mensaje.")
        return

    help_text = (
        "🤖 <b>Comandos Disponibles:</b>\n\n"
        "/start - Iniciar el bot\n"
        "/menu - Abrir el menú del restaurante\n"
        "/mispedidos - Ver el estado de mis pedidos\n"
        "/help - Obtener ayuda\n\n"
        "💡 <b>Tip:</b> Usa el botón de menú (☰) para acceder rápidamente a los comandos."
    )

    await update.message.reply_html(help_text)


def get_bot_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("menu", menu),
        CommandHandler("mispedidos", mis_pedidos),
        CommandHandler("help", help_command),
    ]
