from core.schemas import Recipe, Ingredient
from core.matcher import suggest

def test_suggest_basic():
    r = Recipe(
        id=1, title="Test",
        ingredients=[Ingredient(name="rice"), Ingredient(name="onion")],
        steps=["do x"], time_min=20, tags=["vegan","gluten-free"]
    )
    picks = suggest([r], ["рис", "цибуля"], set())
    assert len(picks) == 1
