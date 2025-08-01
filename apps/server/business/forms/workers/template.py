from typing import Optional

from services.base.worker import BaseWorker
from services.base.cache import BaseCache
from src.connector.s3_connector import S3Connector
from src.logger import logger
from src.schemas.output import Page
from src.schemas.task import (
    TaskModel,
    TaskOperation,
)


class TemplateWorker(BaseWorker):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        models: list = [],
        batch_size: int = 2,
        worker_weight: int = 1,
        cache: Optional[BaseCache] = None,
    ):
        super().__init__(
            name,
            file_connector,
            models=models,
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )

    def is_applicable(self, task: TaskModel) -> bool:
        is_applicable = task.type in [
            TaskOperation.SAVE_TEMPLATE,
            TaskOperation.FORMS,
        ]
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )

        return is_applicable


class TemplateWorkerFeature(TemplateWorker):
    def is_applicable(self, task: TaskModel) -> bool:
        is_applicable = task.type == TaskOperation.VECTORIZE
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )
        return is_applicable


class TemplateWorkerQuery(TemplateWorker):
    def is_applicable(self, task: TaskModel) -> bool:
        is_applicable = task.type == TaskOperation.FORMS
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )
        return is_applicable


class TemplateWorkerSaveTemplate(TemplateWorker):
    def is_applicable(self, task: TaskModel) -> bool:
        is_applicable = task.type == TaskOperation.SAVE_TEMPLATE
        if not is_applicable:
            logger.debug(
                f"[{self.__class__.__name__}]Task {task.id} is not applicable for TemplateWorkerSaveTemplate, type is {task.type}"
            )
            return False
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )

        return is_applicable

    def set_output(self, task, total_pages=-1, pages=...):
        logger.debug(
            f"[{self.__class__.__name__}]Setting output for task {task.id} {task.user_id} with {total_pages} pages"
        )
        return super().set_output(
            task,
            total_pages,
            pages=[Page(page=i) for i in range(total_pages)],
        )
