from src.connector.db_connector import Base, engine

from .task import Task
from .templates import Template
from .annotations import TaskAnnotationBase
from .token import Token
from .ocr_chunks import OcrChunksTable

__all__ = [
    "Task",
    "Base",
    "engine",
    "Template",
    "TaskAnnotationBase",
    "Token",
    "OcrChunksTable",
]

# Base.metadata.create_all(engine)
