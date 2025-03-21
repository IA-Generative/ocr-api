from pydantic import BaseModel
from typing import List, Optional


class TextBox(BaseModel):
    confidence: float
    text: str
    text_region: List[List[int]]


class PaddleOCRResult(BaseModel):
    msg: str
    results: List[List[TextBox]]
    status: str
    images_base64: Optional[List[str]] = None
