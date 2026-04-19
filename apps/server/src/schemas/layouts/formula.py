from pydantic import BaseModel, Field
from typing import Optional


class FormulaBlock(BaseModel):
    type: str = Field("formula", description="Block type identifier.")
    latex: str = Field(..., description="Mathematical expression in valid LaTeX format.")
    confidence: Optional[float] = Field(None, description="Model confidence score for extraction.")
