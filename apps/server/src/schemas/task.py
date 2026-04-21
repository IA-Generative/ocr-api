from enum import StrEnum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict
from src.schemas.input import InputForm
from src.schemas.output import OCRResult


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
    parameters: Optional[dict[str, Any]] = None
    parent_id: Optional[str] = None


class TaskForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[str] = None
    group_id: Optional[str] = None
    type: Optional[str] = None
    status: str
    percentage: Optional[float] = 0.0
    extras: Optional[dict] = None
    input: Optional[InputForm] = None
    output: Optional[OCRResult] = None
    content_hash: Optional[str] = None
    parameters: Optional[dict[str, Any]] = None
    parent_id: Optional[str] = None
    user_id: Optional[str] = None


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
    parameters: Optional[dict[str, Any]] = None
    parent_id: Optional[str] = None
    user_id: Optional[str] = None


class TaskStatus(StrEnum):
    CREATED = "created"  # Tâche instanciée mais pas encore mise en file
    QUEUED = "queued"  # En attente dans une file de traitement
    STARTED = "started"  # A commencé à être traitée
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"  # Traitée avec succès
    FAILED = "failed"  # Erreur fatale
    RETRYING = "retrying"  # En cours de nouvelle tentative après échec
    CANCELED = "canceled"  # Annulée manuellement ou par logique métier
    TIMEOUT = "timeout"  # N’a pas pu terminer dans le temps imparti
    REVOKED = "revoked"  # Révoquée via Celery


class TaskOperation(StrEnum):
    OCR = "ocr"
    DEFAULT = "default"
    SAVE_TEMPLATE = "save_template"
    FORMS = "forms"
    VECTORIZE = "vectorize"
    VLM_OCR = "vlm_ocr"
    PAGE_CLASSIFICATION = "page_classification"
    CHUNK_OCR = "chunk_ocr"
    ENTITY_EXTRACTION = "entity_extraction"
    TEMPLATING_EXTRACTION = "templating_extraction"
    TEMPLATING_FILLING = "templating_filling"


class CeleryTaskName(StrEnum):
    OCR_TASK = "worker.tasks.ocr"
    PAGE_CLASSIFICATION_TASK = "tasks.page_classification"
    PAGE_TEXT_CLASSIFICATION_TASK = "tasks.page_text_classification"
    DISPATCH_TASK = "tasks.dispatch"
    OCR_CHUNK_TASK = "tasks.ocr_chunk"
    ENTITY_EXTRACTION_TASK = "tasks.entity_extraction"
    TEMPLATING_EXTRACTION_TASK = "tasks.templating_extraction"
    TEMPLATING_FILLING_TASK = "tasks.templating_filling"


class TaskStatsGlobal(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    total_tasks: int
    # Clé = status, Valeur = nombre de tâches
    tasks_stats: Dict[TaskStatus, int]
    # Clé = type d'opération, Valeur = nombre de tâches
    tasks_by_type: Dict[str, int] = {}


class TaskStatsUser(TaskStatsGlobal):
    model_config = ConfigDict(from_attributes=True)
    user_id: str


class TaskStats(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    global_stats: TaskStatsGlobal
    user_stats: TaskStatsUser


class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    rank: int
    user_id: str
    task_count: int
    is_me: bool = False


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntry]
    my_rank: int | None = None
    total_participants: int
