from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Segmentation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    start_time: float
    end_time: float
    label: str
    confidence: Optional[float] = None
    text: str


class AudioTranscriptionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    model_name: str
    created_at: int
    updated_at: int
    version: str
    segmentations: list[Segmentation] = Field(default_factory=list, description="List of segmentations")
    transcription_text: str
    extras: Optional[dict] = None
