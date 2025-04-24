from abc import ABC, abstractmethod
from pydantic import BaseModel


class BaseWorker(ABC):
    @abstractmethod
    def process_task(self, task: BaseModel) -> BaseModel: ...
