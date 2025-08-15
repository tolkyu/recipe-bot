from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from app.handlers import _get_session
from core.ai_simple import generate_dish_names, generate_full_recipe

async def ai_menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    s = _get_session(user_id)
    if not s.get("ingredients"):
        await update.message.reply_text("Спочатку додай інгредієнти через /ingredients.")
        return

    await update.message.reply_text("Генерую варіанти страв…")
    try:
        names = generate_dish_names(s["ingredients"], list(s["filters"]), k=6)
    except Exception as e:
        await update.message.reply_text(f"Не вдалось згенерувати меню: {e}")
        return

    if not names:
        await update.message.reply_text("ШІ не запропонував жодної страви. Спробуй змінити інгредієнти.")
        return

    s["ai_menu"] = names
    buttons = [[InlineKeyboardButton(n[:30], callback_data=f"ai_dish:{i}")]
               for i, n in enumerate(names)]
    await update.message.reply_text("Оберіть страву:", reply_markup=InlineKeyboardMarkup(buttons))

async def ai_dish_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = q.from_user.id
    s = _get_session(user_id)
    if not s.get("ai_menu"):
        await q.edit_message_text("Список страв втрачено. Згенеруй заново: /menu")
        return

    try:
        idx = int(q.data.split(":")[1])
        dish_name = s["ai_menu"][idx]
    except Exception:
        await q.edit_message_text("Некоректний вибір. Спробуй ще раз: /menu")
        return

    await q.edit_message_text(f"Готую рецепт для «{dish_name}»…")
    try:
        recipe_text = generate_full_recipe(dish_name, s["ingredients"], list(s["filters"]))
    except Exception as e:
        await q.message.reply_text(f"Не вдалось згенерувати рецепт: {e}")
        return

    await q.message.reply_text(recipe_text)
