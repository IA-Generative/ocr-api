from pydantic import BaseModel, ConfigDict
from typing import List


class BaseBox(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    x: float
    y: float
    width: float
    height: float
    confidence: float


class Bbox(BaseBox):
    text: str


class Box(BaseModel):
    text: str
    text_region: List[List[int]]
    confidence: float
