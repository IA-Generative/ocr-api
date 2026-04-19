from pydantic import BaseModel, Field
from typing import Optional, List


class ImageContent(BaseModel):
    objects: List[str] = Field(..., description="List of visual objects detected in the image.")
    text: List[str] = Field(..., description="All visible text extracted from the image.")
    description: Optional[str] = Field(None, description="Optional overall description of the image content.")
    layout: Optional[str] = Field(None, description="Overall spatial layout description.")
    relationships: List[str] = Field(..., description="Relationships between elements in the image.")


class ImageBlock(BaseModel):
    type: str = Field("image", description="Block type identifier.")
    content: ImageContent = Field(..., description="Structured visual understanding of the image.")
