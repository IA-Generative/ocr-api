from typing import Tuple, Optional
from pydantic import BaseModel


class PredictionOCR(BaseModel):
    confidence: float
    text: str
    text_region: list[float]
    model_version: Optional[str] = None
    extra: Optional[dict] = None
