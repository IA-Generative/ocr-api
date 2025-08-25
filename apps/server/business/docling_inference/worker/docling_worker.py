from typing import Optional

from services.base.worker import BaseWorker
from services.base.cache import BaseCache
from src.connector.s3_connector import S3Connector
from src.logger import logger
from src.schemas.task import (
    TaskModel,
    TaskOperation,
)


class DoclingWorker(BaseWorker):
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
        is_applicable = task.type in [TaskOperation.DOCLING]
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )

        return is_applicable
