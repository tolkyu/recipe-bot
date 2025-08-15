import json
from pathlib import Path
from typing import Iterable
import pandas as pd
from rapidfuzz import process, fuzz
from .schemas import Recipe, Ingredient
from .normalizer import normalize_list, normalize_ingredient_name

PANTRY = {"salt", "black pepper", "olive oil"}  
FUZZ_THRESHOLD = 85

def load_recipes_csv(path: str | Path) -> list[Recipe]:
    df = pd.read_csv(path)
    out = []
    for _, row in df.iterrows():
        ings = [Ingredient(**i) for i in json.loads(row["ingredients"])]
        steps = list(json.loads(row["steps"]))
        tags = list(json.loads(row["tags"]))
        out.append(Recipe(
            id=int(row["id"]),
            title=row["title"],
            ingredients=ings,
            steps=steps,
            time_min=int(row["time_min"]),
            tags=tags
        ))
    return out

def _recipe_norm_names(r: Recipe) -> list[str]:
    return [normalize_ingredient_name(i.name) for i in r.ingredients]

def fuzzy_match(user_set: set[str], recipe_names: list[str]):
    found = set()
    missing = []
    for rname in recipe_names:
        match = process.extractOne(rname, user_set, scorer=fuzz.WRatio)
        if match and match[1] >= FUZZ_THRESHOLD:
            found.add(rname)
        else:
            missing.append(rname)
    return found, missing

def violates_filters(r: Recipe, filters: set[str]) -> bool:
    if "vegan" in filters and "vegan" not in r.tags:
        return True
    if "vegetarian" in filters and ("vegetarian" not in r.tags and "vegan" not in r.tags):
        return True
    if "gluten-free" in filters and "gluten-free" not in r.tags:
        return True
    if "dairy-free" in filters and "dairy-free" not in r.tags:
        return True
    return False

def score_recipe(r: Recipe, user_set: set[str]):
    R = _recipe_norm_names(r)
    M, Miss = fuzzy_match(user_set, R)

    pantry_bonus = 1 if len(Miss) > 0 and all(m in PANTRY for m in Miss) else 0
    hard_missing = 1 if (len(R) > 0 and R[0] in Miss) else 0

    coverage = len(M) / max(1, len(R))
    time_bonus = 1 - min(r.time_min / 90, 1)

    score = 0.55*coverage + 0.15*time_bonus + 0.15*pantry_bonus - 0.15*hard_missing
    return score, M, Miss

def suggest(recipes: Iterable[Recipe], user_ingredients: list[str], filters: set[str], top_k: int = 5):
    U = normalize_list(user_ingredients)
    candidates = []
    for r in recipes:
        if violates_filters(r, filters):
            continue
        s, M, Miss = score_recipe(r, U)
        candidates.append((s, r, M, Miss))
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[:top_k]
