from pydantic import BaseModel
from typing import List


class Box(BaseModel):
    text: str
    text_region: List[List[int]]
    confidence: float
