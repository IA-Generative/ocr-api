from abc import ABC, abstractmethod
from src.schemas.task import TaskModel


class BaseCache(ABC):
    @abstractmethod
    def is_in_cache(self, task: TaskModel) -> bool: ...

    @abstractmethod
    def get_task_from_cache(self, task: TaskModel) -> TaskModel: ...
