import os
import requests

AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.openai.com/v1")
AI_MODEL = os.getenv("AI_MODEL", "gpt-4o-mini")

def _ensure_key():
    if not AI_API_KEY:
        raise RuntimeError("AI_API_KEY is missing in .env")

def _chat(messages, temperature=0.7) -> str:
    _ensure_key()
    headers = {"Authorization": f"Bearer {AI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": AI_MODEL, "messages": messages, "temperature": temperature}
    r = requests.post(f"{AI_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def generate_dish_names(ingredients, filters=None, k=6) -> list[str]:
    flt = ", ".join(filters or []) or "немає"
    ing = ", ".join(ingredients)
    prompt = (
        "Ти шеф-кухар. На основі інгредієнтів українською згенеруй короткий список з "
        f"{k} різних страв (лише назви, по одній у рядку), без нумерації, без пояснень.\n"
        f"Інгредієнти: {ing}\n"
        f"Обмеження/фільтри: {flt}\n"
        "Не використовуй англійську. Лише список назв, по одному варіанту у рядку."
    )
    text = _chat([{"role": "user", "content": prompt}], temperature=0.8)
    names = [line.strip("-• ").strip() for line in text.splitlines() if line.strip()]
    seen, out = set(), []
    for n in names:
        n = n[:64]
        if n and n not in seen:
            seen.add(n); out.append(n)
        if len(out) >= k:
            break
    return out

def generate_full_recipe(dish_name: str, ingredients, filters=None) -> str:
    flt = ", ".join(filters or []) or "немає"
    ing = ", ".join(ingredients)
    prompt = (
        f"Ти шеф-кухар. Користувач обрав страву: «{dish_name}».\n"
        f"Інгредієнти користувача: {ing}\n"
        f"Обмеження/фільтри: {flt}\n\n"
        "Напиши рецепт українською, БЕЗ JSON:\n"
        "— Короткий опис (1–2 речення)\n"
        "— Список інгредієнтів (по рядку, з кількостями у г/мл/шт за потреби)\n"
        "— Покрокове приготування (нумерований список 5–10 кроків)\n"
        "— Орієнтовний час і подачу\n"
        "Уникай англійських слів."
    )
    return _chat([{"role": "user", "content": prompt}], temperature=0.7)
