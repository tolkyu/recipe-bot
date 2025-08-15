import json, re
from pathlib import Path

# завантажуємо синоніми один раз
_SYNONYMS = {}
def _load_synonyms():
    global _SYNONYMS
    p = Path(__file__).parent.parent / "data" / "synonyms.json"
    if p.exists():
        _SYNONYMS = json.loads(p.read_text(encoding="utf-8"))
_load_synonyms()


_STOP_WORDS = r"(свіж(ий|а|е)|молот(ий|а)|терт(ий|а)|копчен(ий|а)|подрібнен(ий|а))"

def normalize_token(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s%\-]", " ", s, flags=re.U)
    s = re.sub(_STOP_WORDS, "", s, flags=re.U)
    s = re.sub(r"\s+", " ", s).strip()
    # мапінг синонімів
    if s in _SYNONYMS:
        s = _SYNONYMS[s]
    return s

def normalize_list(raw: list[str]) -> set[str]:
    out = set()
    for t in raw:
        n = normalize_token(t)
        if n:
            out.add(n)
    return out

def normalize_ingredient_name(name: str) -> str:
    return normalize_token(name)
