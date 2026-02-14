"""Pydantic models for OCR API inputs and outputs."""

from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Task status enum."""
    CREATED = "created"
    QUEUED = "queued"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELED = "canceled"
    TIMEOUT = "timeout"


class TaskOperation(str, Enum):
    """Task operation enum."""
    OCR = "ocr"
    DEFAULT = "default"
    SAVE_TEMPLATE = "save_template"
    FORMS = "forms"
    VECTORIZE = "vectorize"
    VLM_OCR = "vlm_ocr"
    DOCLING = "docling"


class Bbox(BaseModel):
    """Bounding box model."""
    model_config = ConfigDict(from_attributes=True)
    x: float
    y: float
    width: float
    height: float
    text: str
    confidence: Optional[float] = None


class Checkbox(BaseModel):
    """Checkbox model."""
    model_config = ConfigDict(from_attributes=True)
    x: float
    y: float
    width: float
    height: float
    confidence: Optional[float] = None
    is_checked: bool = False


class Layout(BaseModel):
    """Layout model."""
    model_config = ConfigDict(from_attributes=True)
    type: str
    bbox: Optional[Bbox] = None


class RegionOfInterest(BaseModel):
    """Region of interest model."""
    model_config = ConfigDict(from_attributes=True)
    interest_zone: list[Bbox] = Field(default_factory=list)
    labels: Optional[str] = None


class InputForm(BaseModel):
    """Input form model."""
    model_config = ConfigDict(from_attributes=True)
    storage_file_path: str
    raw_filename: str
    content_type: str
    ext: str
    size: int
    process_type: str = "DEFAULT"
    group_id: Optional[str] = None
    interest_zone: Optional[list[RegionOfInterest]] = Field(default_factory=list)


class FormEntry(BaseModel):
    """Form entry model."""
    model_config = ConfigDict(from_attributes=True)
    field_name: Optional[str] = None
    field_value: Optional[str] = None


class Page(BaseModel):
    """Page model."""
    model_config = ConfigDict(from_attributes=True)
    page: int
    page_url: Optional[str] = None
    boxes: List[Bbox] = Field(default_factory=list)
    layouts: List[Layout] = Field(default_factory=list)
    checkboxes: List[Checkbox] = Field(default_factory=list)
    form_entries: List[FormEntry] = Field(default_factory=list)


class OCRResult(BaseModel):
    """OCR result model."""
    model_config = ConfigDict(from_attributes=True)
    type: str
    model_name: str
    created_at: int
    updated_at: int
    version: str
    total_pages: int
    pages: List[Page]
    extras: Optional[dict] = None
    text: Optional[str] = ""


class TaskModel(BaseModel):
    """Task model."""
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


class Health(BaseModel):
    """Health check model."""
    model_config = ConfigDict(from_attributes=True)
    name: str
    version: str
    up_time: str
    status: str
    dependencies: Optional[List["Health"]] = Field(default_factory=list)


class ProcessResponse(BaseModel):
    """Process response model."""
    model_config = ConfigDict(from_attributes=True)
    page_content: str
    metadata: Dict[str, Any]
