from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.schemas.box import Bbox


class RegionOfInterest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    interest_zone: list[Bbox] = []
    labels: Optional[str] = None


class InputForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    storage_file_path: str
    raw_filename: str
    content_type: str
    ext: str
    size: int
    process_type: str = "DEFAULT"
    group_id: Optional[str] = None
    interest_zone: Optional[list[RegionOfInterest]] = Field(default_factory=list)
    parameters: Optional[dict] = Field(default_factory=dict)
