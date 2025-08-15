from typing import Dict, Any
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

_sessions: Dict[int, Dict[str, Any]] = {}

def _get_session(user_id: int) -> Dict[str, Any]:
    if user_id not in _sessions:
        _sessions[user_id] = {
            "filters": set(),
            "ingredients": [],
            "ai_menu": [],
            "awaiting_ingredients": False,  
        }
    return _sessions[user_id]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! Я згенерую рецепт(и) з того, що є в холодильнику.\n"
        "1) /ingredients — надішли перелік через кому (напр.: курка, рис, броколі)\n"
        "2) /menu — запропоную варіанти страв (ШІ)\n"
        "Фільтри: /filters"
    )

async def filters_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = _get_session(user_id)
    current = s["filters"]
    mk = lambda key, label: InlineKeyboardButton(
        ("✅ " if key in current else "⬜️ ") + label, callback_data=f"f:{key}"
    )
    buttons = [
        [mk("vegan","Vegan")],
        [mk("vegetarian","Vegetarian")],
        [mk("gluten-free","Gluten-free")],
        [mk("dairy-free","Dairy-free")],
    ]
    await update.message.reply_text("Перемикачі фільтрів:", reply_markup=InlineKeyboardMarkup(buttons))

async def filters_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    s = _get_session(user_id)
    _, key = q.data.split(":")
    if key in s["filters"]:
        s["filters"].remove(key); mark = "вимкнено"
    else:
        s["filters"].add(key); mark = "увімкнено"
    await q.edit_message_text(f"Фільтр '{key}' {mark}. Поточні: {', '.join(sorted(s['filters'])) or 'немає'}")

async def ingredients_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = _get_session(update.effective_user.id)
    s["awaiting_ingredients"] = True
    print(">>> /ingredients TRIGGERED")  
    await update.message.reply_text("Введи інгредієнти через кому (напр.: курка, рис, броколі):")

async def any_update_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Ловимо БУДЬ-ЯКЕ оновлення. Якщо очікуємо інгредієнти і прийшов текст — зберігаємо.
    ВАЖЛИВО: ігноруємо команди (тексти, що починаються з '/'), щоб не зберігати '/ingredients'.
    """
    msg = getattr(update, "message", None)
    if not msg:
        return

    s = _get_session(update.effective_user.id)

    if not s.get("awaiting_ingredients"):
        return

    text = (msg.text or "").strip()
    if not text:
        return

    if text.startswith("/"):
        return

    items = [t.strip() for t in text.split(",") if t.strip()]
    s["ingredients"] = items
    s["awaiting_ingredients"] = False
    print(">>> SAVED INGREDIENTS:", items)  # лог у термінал по пріколу шоб бачити що збереглось

    await msg.reply_text(
        f"Готово. Я запам’ятав {len(items)} інгредієнтів: {', '.join(items) or '—'}.\n"
        "Тепер надішли /menu (або /suggest), щоб отримати варіанти страв."
    )

__all__ = [
    "_get_session", "start", "filters_cmd", "filters_toggle",
    "ingredients_start", "any_update_handler",
]
