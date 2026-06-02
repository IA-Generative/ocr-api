from typing import Optional
import shutil
import tempfile
from services.base.worker import BaseWorker
from services.base.model import BaseModelPrediction
from services.base.cache import BaseCache
from services.utils.lazy_file import LazyFileImageList
from src.connector.s3_connector import S3Connector
from src.logger import logger
from business.extractions.models.file_extraction import FileHandlerExtractionModel
from src.schemas.task import TaskModel
from business.extractions.models.content_types import (
    EXCEL_CONTENT_TYPE,
    DOCX_CONTENT_TYPE,
    CSV_CONTENT_TYPE,
    ODT_CONTENT_TYPE,
    ODS_CONTENT_TYPE,
    ODP_CONTENT_TYPE,
)

from pathlib import Path


class BaseFileWorker(BaseWorker):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        models: list[BaseModelPrediction] = [],
        batch_size: int = 2,
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

    def predict_on_pages(
        self,
        task: TaskModel,
        pages: list,
        save_image: bool = True,
    ) -> TaskModel:
        # For file workers, we ignore the pages input and process the whole file
        return super().predict_on_pages(task, pages=pages, save_image=save_image)

    def is_applicable(self, task: TaskModel) -> bool:
        if not task.input or not task.input.content_type:
            return False

        return task.input.content_type in (
            ODT_CONTENT_TYPE
            + ODS_CONTENT_TYPE
            + ODP_CONTENT_TYPE
            + DOCX_CONTENT_TYPE
            + EXCEL_CONTENT_TYPE
            + CSV_CONTENT_TYPE
        )

    def transform_content(self, task: TaskModel, content: bytes | str) -> LazyFileImageList:
        if not task.input or not task.input.raw_filename:
            raise ValueError("Task input path is required for file processing")

        # Determine the expected file extension from the task metadata.
        # The downloaded content path (from S3) has no extension, which makes
        # liteparse fail with "unsupported file format: .".
        suffix = task.input.ext or Path(task.input.raw_filename).suffix
        if suffix and not suffix.startswith("."):
            suffix = f".{suffix}"
        logger.debug(
            f"[worker {self.name}] {task.id} - transform_content "
            f"raw_filename={task.input.raw_filename} ext={task.input.ext} suffix={suffix}"
        )
        if not suffix:
            logger.error(
                f"[worker {self.name}] {task.id} - missing file extension for raw_filename={task.input.raw_filename}"
            )
            raise ValueError(f"Cannot determine file extension for {task.input.raw_filename}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            if isinstance(content, bytes):
                tmp_file.write(content)
            else:
                with open(content, "rb") as src:
                    shutil.copyfileobj(src, tmp_file)
            tmp_file.flush()
            content_path = tmp_file.name
        logger.debug(f"[worker {self.name}] {task.id} - content ready at {content_path}")

        images = LazyFileImageList(content_path, dpi=200, fmt="jpeg")
        for model in self.models:
            if isinstance(model, FileHandlerExtractionModel):
                model.parser_result = images.parser.parse(content_path)
        logger.debug(f"[worker {self.name}] {task.id} - parsed {len(images)} page(s) from {content_path}")
        return images


class CSVWorker(BaseFileWorker): ...


class DocxWorker(BaseFileWorker): ...


class OdtWorker(BaseFileWorker): ...


class OdpWorker(BaseFileWorker): ...


class OdsWorker(BaseFileWorker): ...


class XlsxWorker(BaseFileWorker): ...
