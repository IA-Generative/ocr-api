from pydantic import BaseModel, ConfigDict
from typing import List


class BaseBox(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    x: float
    y: float
    width: float
    height: float
    confidence: float


class Checkbox(BaseBox):
    is_checked: bool


class Bbox(BaseBox):
    text: str
    orientation: int | None = None


class PredictText(BaseModel):
    text: str
    confidence: float


class Box(BaseModel):
    text: str
    text_region: List[List[int]]
    confidence: float
