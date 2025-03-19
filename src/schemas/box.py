from typing import List, Optional
from pydantic import BaseModel


class Box(BaseModel):
    text: str
    text_region: List[List[int]]
    confidence: float
