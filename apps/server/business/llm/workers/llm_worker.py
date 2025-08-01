from services.base.worker import BaseWorker
from src.logger import logger
from src.schemas.task import (
    TaskModel,
    TaskOperation,
)


class VLMFormWorker(BaseWorker):
    def is_applicable(self, task: TaskModel) -> bool:
        is_applicable = task.type == TaskOperation.FORMS
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )
        return is_applicable


class VLMOcrWorker(BaseWorker):
    def is_applicable(self, task: TaskModel) -> bool:
        is_applicable = task.type == TaskOperation.VLM_OCR
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )
        return is_applicable
