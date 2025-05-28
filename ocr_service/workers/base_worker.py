from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type
from pydantic import BaseModel
from celery import Celery

T = TypeVar("T", bound=BaseModel)


class BaseWorker(ABC, Generic[T]):
    def __init__(self, celery_app: Celery, task_model: Type[T]):
        self.celery_app = celery_app
        self.task_model = task_model
        self._register_task()

    @abstractmethod
    def process_task(self, task: T) -> T: ...

    def _register_task(self):
        @self.celery_app.task(name=f"{self.__class__.__name__}.run")
        def task_runner(task_dict):
            task_instance = self.task_model(**task_dict)
            result = self.process_task(task_instance)
            return result.model_dump()

        self._celery_task = task_runner

    def delay(self, task: T):
        return self._celery_task.delay(task.model_dump())

    def apply_async(self, task: T, **kwargs):
        return self._celery_task.apply_async(args=[task.model_dump()], **kwargs)
