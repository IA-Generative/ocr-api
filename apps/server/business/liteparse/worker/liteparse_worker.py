from typing import List, Optional

from PIL import Image

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

    def predict_on_pages(self, task: TaskModel, pages: List[Image.Image], save_image: bool = True) -> TaskModel:
        # `pages` here are actually raw file bytes, not PIL images — LiteparseExtractionModel
        # already uploads its own page screenshots and sets Page.page_url itself,
        # so skip BaseWorker's generic image.save() upload step.
        return super().predict_on_pages(task=task, pages=pages, save_image=False)
