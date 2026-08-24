from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from ocr_sdk.schemas.box import Bbox


class ProcessType(str, Enum):
    DEFAULT = "default"
    OCR = "ocr"
    TEMPLATE = "template"
    QUERY = "query"


class RegionOfInterest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    interest_zone: list[Bbox] = []
    labels: Optional[str] = None


class InputForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    storage_file_path: Optional[str] = None
    raw_filename: str
    content_type: str
    ext: str
    size: int
    process_type: str = "DEFAULT"
    group_id: Optional[str] = None
    interest_zone: Optional[list[RegionOfInterest]] = Field(default_factory=list)
    source_url: Optional[str] = Field(
        default=None,
        description="URL externe (ex: YouTube) quand il n'y a pas de fichier stocké",
    )
