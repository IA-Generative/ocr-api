from typing import Optional

from services.base.worker import BaseWorker
from services.base.model import BaseModelPrediction
from services.base.cache import BaseCache
from src.connector.s3_connector import S3Connector
from src.logger import logger
from src.schemas.task import (
    TaskModel,
    TaskOperation,
)
from business.extractions.models.csv_extraction import (
    CSV_CONTENT_TYPE,
    CSVExtractionModel,
)
from business.extractions.models.docx_extraction import (
    DOCX_CONTENT_TYPE,
    DocxExtractionModel,
)
from business.extractions.models.excel_extraction import ExcelExtractionModel
from business.extractions.models.excel_extraction import EXCEL_CONTENT_TYPE
from business.extractions.models.libre_extraction import (
    ODT_CONTENT_TYPE,
    ODTExtractionModel,
    ODS_CONTENT_TYPE,
    OdsExtractionModel,
    ODP_CONTENT_TYPE,
    OdpExtractionModel,
)


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
        save_image: bool = False,
    ) -> TaskModel:
        # For file workers, we ignore the pages input and process the whole file
        return super().predict_on_pages(task, pages=pages, save_image=save_image)

    def transform_content(self, task: TaskModel, content: bytes) -> list[bytes]:
        for model in self.models:
            if not getattr(model, "is_applicable", lambda x: False)(task):
                logger.debug(f"[{self.__class__.__name__}] Using model {model.__class__.__name__} for task {task.id}")
                raise ValueError(
                    f"No applicable model found for task {task.id} with content type {task.input.content_type}"
                )
        if isinstance(content, str):
            with open(content, "rb") as f:
                content = f.read()
                return [content]

        return [content]


class CSVWorker(BaseFileWorker):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        batch_size: int = 2,
        worker_weight: float = 1,
        cache: Optional[BaseCache] = None,
    ):
        super().__init__(
            name,
            file_connector,
            models=[CSVExtractionModel()],
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )

    def is_applicable(self, task: TaskModel) -> bool:
        if not task.input or not task.input.content_type:
            return False
        is_applicable = task.type in [TaskOperation.DEFAULT] and task.input.content_type in CSV_CONTENT_TYPE
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )

        return is_applicable


class DocxWorker(BaseFileWorker):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        batch_size: int = 2,
        worker_weight: float = 1,
        cache: Optional[BaseCache] = None,
    ):
        super().__init__(
            name,
            file_connector,
            models=[DocxExtractionModel()],
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )

    def is_applicable(self, task: TaskModel) -> bool:
        if not task.input or not task.input.content_type:
            return False
        is_applicable = task.type in [TaskOperation.DEFAULT] and task.input.content_type in DOCX_CONTENT_TYPE
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )

        return is_applicable


class OdtWorker(BaseFileWorker):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        batch_size: int = 2,
        worker_weight: float = 1,
        cache: Optional[BaseCache] = None,
    ):
        super().__init__(
            name,
            file_connector,
            models=[ODTExtractionModel()],
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )

    def is_applicable(self, task: TaskModel) -> bool:
        is_applicable = task.type in [TaskOperation.DEFAULT] and task.input.content_type in ODT_CONTENT_TYPE
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )

        return is_applicable


class OdpWorker(BaseFileWorker):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        batch_size: int = 2,
        worker_weight: float = 1,
        cache: Optional[BaseCache] = None,
    ):
        super().__init__(
            name,
            file_connector,
            models=[OdpExtractionModel()],
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )

    def is_applicable(self, task: TaskModel) -> bool:
        if not task.input or not task.input.content_type:
            return False
        is_applicable = task.type in [TaskOperation.DEFAULT] and task.input.content_type in ODP_CONTENT_TYPE
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )

        return is_applicable


class OdsWorker(BaseFileWorker):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        batch_size: int = 2,
        worker_weight: float = 1,
        cache: Optional[BaseCache] = None,
    ):
        super().__init__(
            name,
            file_connector,
            models=[OdsExtractionModel()],
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )

    def is_applicable(self, task: TaskModel) -> bool:
        if not task.input or not task.input.content_type:
            return False

        is_applicable = task.type in [TaskOperation.DEFAULT] and task.input.content_type in ODS_CONTENT_TYPE
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )

        return is_applicable


class XlsxWorker(BaseFileWorker):
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        batch_size: int = 2,
        worker_weight: float = 1,
        cache: Optional[BaseCache] = None,
    ):
        super().__init__(
            name,
            file_connector,
            models=[ExcelExtractionModel()],
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )

    def is_applicable(self, task: TaskModel) -> bool:
        if not task.input or not task.input.content_type:
            return False
        is_applicable = task.type in [TaskOperation.DEFAULT] and task.input.content_type in EXCEL_CONTENT_TYPE
        logger.debug(
            f"[{self.__class__.__name__}]Task {task.id} is_applicable: {is_applicable} for process type {task.type}"
        )

        return is_applicable
