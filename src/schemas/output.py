from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from src.schemas.box import Bbox


class Page(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    page: int
    page_url : Optional[str] = None
    boxes: List[Bbox]


class OCRResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    model_name: str
    created_at: int
    updated_at: int
    version: str
    total_pages: int
    pages: List[Page]
    extras: Optional[dict] = None
