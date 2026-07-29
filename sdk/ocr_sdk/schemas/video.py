from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

from ocr_sdk.schemas.audio import AudioTranscriptionResult


class VideoSegmentation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    start_time: float
    end_time: float
    label: str
    confidence: Optional[float] = None
    description: str


class VideoDescriptionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    model_name: str
    created_at: int
    updated_at: int
    version: str
    duration: float
    segmentations: list[VideoSegmentation] = Field(
        default_factory=list, description="List of visual segment descriptions"
    )
    audio_transcription: Optional[AudioTranscriptionResult] = Field(
        default=None, description="Transcription of the video's audio track"
    )
    description: str = Field(default="", description="Global description of the video content")
    extras: Optional[dict] = None
