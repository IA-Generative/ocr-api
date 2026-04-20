from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.schemas.box import Bbox
from src.schemas.classification import Model
from enum import StrEnum


class RegionOfInterest(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    interest_zone: list[Bbox] = []
    labels: Optional[str] = None


class EntityType(StrEnum):
    TEXT = "text"
    DATE = "date"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    EMAIL = "email"
    URL = "url"
    PHONE_NUMBER = "phone_number"


class EntityDefinition(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    definition: str
    entity_type: EntityType = EntityType.TEXT
    formats: Optional[list[str]] = Field(default_factory=list)
    exemples: Optional[list[str]] = Field(default_factory=list)


class EntityCreateDefinition(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    definition: str | None = None
    entity_type: EntityType = EntityType.TEXT
    formats: Optional[list[str]] = Field(default_factory=list)
    exemples: Optional[list[str]] = Field(default_factory=list)


class ParameterEntityDefinition(EntityDefinition):
    entities_definitions: Optional[list[EntityDefinition]] = Field(default_factory=list)


class EntityPrediction(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    entity_name: str
    confidence: float
    value: Optional[str] = None
    bbox: Optional[list[Bbox]] = Field(default_factory=list)
    pages: Optional[list[int]] = Field(default_factory=list)


class EntityExtractionResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    entities: list[EntityPrediction] = Field(default_factory=list)


class EntityExtractionResultWithModel(EntityExtractionResult):
    model: Model
