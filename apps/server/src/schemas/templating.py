from pydantic import BaseModel, ConfigDict, Field
from typing import List
from src.schemas.entity import EntityCreateDefinition
from src.schemas.box import BaseBox
from uuid import uuid4


class TemplatingExtractionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    valid_fields: List[str] = Field(default_factory=list, description="Form entries with valid values")
    invalid_fields: List[str] = Field(default_factory=list, description="Form entries with invalid values")


class EntityZone(BaseModel):
    entity_definition: EntityCreateDefinition
    boxes: BaseBox | None


class TemplatingModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    user_id: str | None = None
    group_id: str

    source_file: str
    source_task_id: str | None = None
    extracting_status: str | None = None
    total_page: int
    created_at: int
    updated_at: int
    entity_zone: list[EntityZone] | None = Field(default_factory=list)
    entity_names: TemplatingExtractionResult | None = None

    extras: dict | None = None


class TemplatingCreateModel(BaseModel):
    id: str | None = str(uuid4())
    name: str
    description: str
    group_id: str
    user_id: str | None = None

    source_file: str
    source_task_id: str | None = None
    total_page: int = 1
    entity_zone: list[EntityZone] | None = Field(default_factory=list)
    entity_names: TemplatingExtractionResult | None = None

    extras: dict | None = None


class TemplatingUpdateModel(BaseModel):
    name: str | None = None
    description: str | None = None

    source_file: str | None = None
    source_task_id: str | None = None
    total_page: int | None = None
    entity_zone: list[EntityZone] | None = Field(default_factory=list)
    entity_names: TemplatingExtractionResult | None = None

    extras: dict | None = None
