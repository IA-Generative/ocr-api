from typing import Optional

from services.base.worker import BaseWorker
from services.base.cache import BaseCache
from src.connector.s3_connector import S3Connector
from src.logger import logger
from src.schemas.task import TaskModel, TaskOperation

from business.liteparse.models.liteparse_model import LITEPARSE_CONTENT_TYPES


class LiteparseWorker(BaseWorker):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        models: list = [],
        batch_size: int = 1,
        worker_weight: float = 1,
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
        is_applicable = task.type in [TaskOperation.DEFAULT] and task.input.content_type in LITEPARSE_CONTENT_TYPES
        logger.debug(
            f"[{self.__class__.__name__}] Task {task.id} is_applicable={is_applicable} "
            f"type={task.type} content_type={task.input.content_type}"
        )
        return is_applicable

    def transform_content(self, task: TaskModel, content: bytes) -> list[bytes]:
        """Return the raw file bytes directly — LiteParse handles format detection."""
        if isinstance(content, str):
            with open(content, "rb") as f:
                content = f.read()
        return [content]
