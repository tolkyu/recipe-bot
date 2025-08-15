from pydantic import BaseModel
from typing import List, Optional

class Ingredient(BaseModel):
    name: str
    qty: float | int | None = None
    unit: Optional[str] = None
    optional: bool = False

class Recipe(BaseModel):
    id: int
    title: str
    ingredients: List[Ingredient]
    steps: List[str]
    time_min: int
    tags: List[str]
