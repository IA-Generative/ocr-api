from pydantic import BaseModel, ConfigDict
from typing import List


class Bbox(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    x: float
    y: float
    width: float
    height: float
    confidence: float
    text: str


class Box(BaseModel):
    text: str
    text_region: List[List[int]]
    confidence: float
