from core.normalizer import normalize_list

def test_normalize():
    raw = ["Помідори", "  цибуля  ", "кабачок свіжий", "вершки"]
    n = normalize_list(raw)
    assert "tomato" in n or "помідор" in n  # залежно від синонімів
    assert "onion" in n
