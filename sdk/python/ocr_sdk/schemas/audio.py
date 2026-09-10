from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class Segmentation(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    start_time: float
    end_time: float
    label: str
    confidence: Optional[float] = None
    text: str


class LanguageTranscript(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    language: str = Field(description="Code langue (ex: fr, en, ja)")
    is_original: bool = Field(
        default=False, description="Langue parlée d'origine de la vidéo"
    )
    segmentations: list[Segmentation] = Field(default_factory=list)
    text: str = ""


class AudioTranscriptionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: str
    model_name: str
    created_at: int
    updated_at: int
    version: str
    segmentations: list[Segmentation] = Field(
        default_factory=list,
        description="Segments de la transcription retenue par défaut",
    )
    transcription_text: str
    transcripts: list[LanguageTranscript] = Field(
        default_factory=list,
        description="Toutes les langues de sous-titres récupérées (dont la langue originale)",
    )
    extras: Optional[dict] = None
