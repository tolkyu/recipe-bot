import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)
from dotenv import load_dotenv
from loguru import logger

from app.handlers import (
    start, filters_cmd, filters_toggle,
    ingredients_start, any_update_handler,
)
from app.handlers_ai import ai_menu_cmd, ai_dish_pick

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
AI_KEY = os.getenv("AI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://твій-сервіс.onrender.com

if not TOKEN:
    raise RuntimeError("❌ TELEGRAM_TOKEN is missing in .env")
if not AI_KEY:
    raise RuntimeError("❌ AI_API_KEY is missing in .env")
if not WEBHOOK_URL:
    raise RuntimeError("❌ WEBHOOK_URL is missing in .env")

app_flask = Flask(__name__)
application = Application.builder().token(TOKEN).build()

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("filters", filters_cmd))
application.add_handler(CallbackQueryHandler(filters_toggle, pattern=r"^f:"))

application.add_handler(CommandHandler(["ingredients", "ingridients"], ingredients_start), group=0)
application.add_handler(MessageHandler(filters.Regex(r"^/(ingredients|ingridients)(@\w+)?$"), ingredients_start), group=0)
application.add_handler(MessageHandler(filters.ALL, any_update_handler), group=1)

application.add_handler(CommandHandler("menu", ai_menu_cmd), group=2)
application.add_handler(CommandHandler("suggest", ai_menu_cmd), group=2)
application.add_handler(CallbackQueryHandler(ai_dish_pick, pattern=r"^ai_dish:\d+$"), group=2)


@app_flask.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    """Тут Telegram надсилає оновлення."""
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200


@app_flask.route("/set_webhook", methods=["GET"])
def set_webhook():
    """Встановлює webhook при першому деплої."""
    webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
    success = application.bot.set_webhook(webhook_url)
    if success:
        return f"Webhook set to {webhook_url}", 200
    return "Webhook setup failed", 500


if __name__ == "__main__":
    logger.info("🚀 Starting bot via Flask + Webhook...")
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
