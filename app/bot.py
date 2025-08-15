import os
from pathlib import Path

from dotenv import load_dotenv
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

from loguru import logger
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)
import requests

from app.handlers import (
    start, filters_cmd, filters_toggle,
    ingredients_start, any_update_handler,
)
from app.handlers_ai import ai_menu_cmd, ai_dish_pick


def _delete_webhook(token: str) -> None:
    """Щоб не ловити Conflict, стираємо webhook перед стартом polling."""
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/deleteWebhook", timeout=10)
        if r.ok:
            logger.info("Webhook deleted (ok).")
        else:
            logger.warning(f"Webhook delete returned {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.warning(f"Webhook delete failed: {e}")

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    ai_key = os.getenv("AI_API_KEY")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is missing in .env")
    if not ai_key:
        raise RuntimeError("AI_API_KEY is missing in .env")

    _delete_webhook(token)

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("filters", filters_cmd))
    app.add_handler(CallbackQueryHandler(filters_toggle, pattern=r"^f:"))

    app.add_handler(CommandHandler(["ingredients", "ingridients"], ingredients_start), group=0)
    app.add_handler(MessageHandler(filters.Regex(r"^/(ingredients|ingridients)(@\w+)?$"), ingredients_start), group=0)

    app.add_handler(MessageHandler(filters.ALL, any_update_handler), group=1)

    app.add_handler(CommandHandler("menu", ai_menu_cmd), group=2)
    app.add_handler(CommandHandler("suggest", ai_menu_cmd), group=2)
    app.add_handler(CallbackQueryHandler(ai_dish_pick, pattern=r"^ai_dish:\d+$"), group=2)

    logger.info("Bot is starting (long polling)...")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
