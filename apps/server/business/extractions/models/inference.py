from abc import abstractmethod
from services.base.model import BaseModelPrediction


from src.schemas.task import TaskModel

from langchain_community.document_loaders import (
    UnstructuredPowerPointLoader,
    TextLoader,
)


class FileExtractionModel(BaseModelPrediction):
    def __init__(self): ...

    @abstractmethod
    def is_applicable(self, task: TaskModel) -> bool: ...


class PPTXExtractionModel(FileExtractionModel):
    def __init__(self):
        self.loader = UnstructuredPowerPointLoader

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation"


class TextExtractionModel(FileExtractionModel):
    def __init__(self):
        self.loader = TextLoader

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type == "text/plain"
