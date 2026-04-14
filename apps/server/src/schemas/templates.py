from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict
from src.schemas.input import RegionOfInterest


class TemplateModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None
    source_file: str
    source_task_id: Optional[str] = None
    page_number: int = 0
    vector: Optional[list[float]] = None
    model_name: Optional[str] = None
    vector_size: Optional[int] = None
    created_at: int
    updated_at: int
    extras: Optional[Dict[str, Any]] = None
    interest_zone: Optional[RegionOfInterest] = None


class TemplateForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None
    source_file: str
    source_task_id: Optional[str] = None
    page_number: int = 0
    vector: Optional[list[float]] = None
    model_name: Optional[str] = None
    vector_size: Optional[int] = None
    extras: Optional[Dict[str, Any]] = None
    interest_zone: Optional[RegionOfInterest] = None


class TemplateUpdateForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: Optional[str] = None
    group_id: Optional[str] = None
    description: Optional[str] = None
    source_file: Optional[str] = None
    source_task_id: Optional[str] = None
    page_number: Optional[int] = None
    vector: Optional[list[float]] = None
    model_name: Optional[str] = None
    vector_size: Optional[int] = None
    extras: Optional[Dict[str, Any]] = None
    interest_zone: Optional[RegionOfInterest] = None
