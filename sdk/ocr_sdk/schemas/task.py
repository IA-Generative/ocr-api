from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict

from ocr_sdk.schemas.input import InputForm
from ocr_sdk.schemas.output import OCRResult


class TaskModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    group_id: Optional[str] = None
    type: str
    status: str = "queued"
    percentage: Optional[float] = 0.0
    input: Optional[InputForm] = None
    output: Optional[OCRResult] = None
    created_at: int
    updated_at: int
    extras: Optional[Dict[str, Any]] = None
    position: Optional[int] = None
    content_hash: Optional[str] = None


class TaskForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id: Optional[str] = None
    type: Optional[str] = None
    status: str
    percentage: Optional[float] = 0.0
    extras: Optional[dict] = None
    input: Optional[InputForm] = None
    output: Optional[OCRResult] = None
    content_hash: Optional[str] = None


class TaskUpdateForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    percentage: Optional[float] = 0.0
    extras: Optional[dict] = None
    input: Optional[InputForm] = None
    output: Optional[OCRResult] = None
    content_hash: Optional[str] = None


class TaskStatus(str, Enum):
    CREATED = "created"  # Tâche instanciée mais pas encore mise en file
    QUEUED = "queued"  # En attente dans une file de traitement
    STARTED = "started"  # A commencé à être traitée
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"  # Traitée avec succès
    FAILED = "failed"  # Erreur fatale
    RETRYING = "retrying"  # En cours de nouvelle tentative après échec
    CANCELED = "canceled"  # Annulée manuellement ou par logique métier
    TIMEOUT = "timeout"  # N’a pas pu terminer dans le temps imparti


class TaskOperation(str, Enum):
    OCR: str = "ocr"
    DEFAULT: str = "default"
    SAVE_TEMPLATE: str = "save_template"
    FORMS: str = "forms"
    VECTORIZE: str = "vectorize"
    VLM_OCR: str = "vlm_ocr"
    DOCLING: str = "docling"
