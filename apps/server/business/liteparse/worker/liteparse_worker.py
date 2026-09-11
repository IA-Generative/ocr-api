from typing import List, Optional

from PIL import Image

from services.base.worker import BaseWorker
from services.base.cache import BaseCache
from src.connector.s3_connector import S3Connector
from src.logger import logger
from src.schemas.output import Page
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
        """`pages` here is always `[raw_file_bytes]` (see `transform_content` above) —
        a single uploaded file, not one item per document page. `LiteparseExtractionModel
        .batch_predict` internally expands that one file into any number of real pages/
        slides (one per DOCX page, PPTX slide, CSV...). `BaseWorker.predict_on_pages` /
        `_predict_on_ocr_batch` assume a strict 1-input-item : 1-output-page mapping and
        only ever keep the first page of that expansion, silently dropping the rest for
        any multi-page/multi-slide document — override the whole thing instead of
        letting the base class truncate it.

        LiteparseExtractionModel also already uploads its own page screenshots and sets
        `Page.page_url` itself, so this skips BaseWorker's generic image.save() upload
        step the same way the previous implementation did (there is no `save_image` path
        here at all now, since we never call `_upload_page_image`).
        """
        task = self.set_output(task=task, total_pages=len(pages))
        task.output.pages = []
        task.output.text = ""

        partial_result: List[Page] = []
        for model in self.models:
            model.set_current_task(task)
            partial_result = model.batch_predict(images=pages, pages=partial_result)

        task.output.pages = partial_result
        task.output.total_pages = len(partial_result)

        if not partial_result:
            task.output.set_text()
            return task

        return self._checkpoint_progress(task, len(partial_result))
