import hashlib
import time
from typing import List, Optional

from PIL import Image

from services.base.model import BaseModelPrediction
from services.base.cache import BaseCache
from services.utils.lazy_pdf import LazyPdfImageList
from src import __name__, __version__
from src.connector.s3_connector import S3Connector
from src.logger import logger
from src.schemas.output import OCRResult, Page
from src.schemas.task import TaskModel, TaskStatus, TaskUpdateForm, task_table
from io import BytesIO


class EmptyContentException(Exception): ...


class FileNotSupported(Exception): ...


def hash_file(file_path: str):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for bloc in iter(lambda: f.read(4096), b""):
            h.update(bloc)
    return h.hexdigest()


class BaseWorker:
    def __init__(
        self,
        name: str,
        file_connector: S3Connector,
        models: List[BaseModelPrediction],
        batch_size: int = 2,
        worker_weight: float = 1,
        cache: Optional[BaseCache] = None,
    ):
        self.name = name
        self.file_connector = file_connector
        self.models = models
        self.worker_weight = worker_weight
        self.batch_size = batch_size
        self.cache = cache

    def set_extras(self, task: TaskModel) -> TaskModel:
        task.extras = task.extras if task.extras is not None else {}
        return task

    def get_content_file(self, task: TaskModel) -> str:
        task = self.set_output(task=task)
        try:
            logger.info(f"{task.id} load file ")
            content = self.file_connector.get_by_task_id(user_id=task.user_id, task_id=task.id)
            logger.info(f"{task.id} loaded")

        except Exception as e:
            task.extras["error"] = str(e)
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(status=TaskStatus.FAILED.value, percentage=0, extras=task.extras),
            )
            logger.error(str(e))
            raise

        if content is None:
            task.extras["error"] = f"No content found for task : {task.id}"
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(status=TaskStatus.FAILED.value, percentage=0, extras=task.extras),
            )
            logger.error(f"No content found for task : {task.id}")
            raise EmptyContentException(f"No content found for task : {task.id}")
        return content

    def transform_content(self, task: TaskModel, content: bytes) -> List[Image.Image]:
        task = self.set_output(task=task)

        content_type: str = task.input.content_type
        logger.debug(f"content-type : {content_type}")
        filename = task.input.raw_filename

        if content_type.startswith("image/"):
            pages = [Image.open(content).convert("RGB")]

        elif content_type == "application/pdf":
            t_convert = time.time()
            logger.debug(f"{task.id} - {filename} convert to image")
            logger.info(79 * "*")

            pages = LazyPdfImageList(content)
            t_convert = time.time() - t_convert
            logger.debug(f"{task.id} - {filename} convert to image nb pages {len(pages)} into {t_convert}")

        else:
            logger.error(f"Unsupported file type {task.extras}")
            task.extras["error"] = f"Unsupported file type {task.extras}"
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(status=TaskStatus.FAILED.value, percentage=0, extras=task.extras),
            )
            raise FileNotSupported(f"Unsupported file type {content_type}")

        return pages

    def predict_on_pages(self, task: TaskModel, pages: List[Image.Image]) -> TaskModel:
        task = self.set_output(task=task, total_pages=len(pages))
        filename = task.input.raw_filename
        client_s3 = self.file_connector.client

        task.output.text = ""
        for i in range(0, len(pages), self.batch_size):
            t_predict = time.time()
            batch = pages[i : i + self.batch_size]
            logger.debug(f"{filename} for task {task.id}")
            partial_result: List[Page] = task.output.pages

            for model in self.models:
                logger.debug(f"[task-id {task.id}][model {model.__class__.__name__}]")
                t = time.time()
                partial_result: List[Page] = model.batch_predict(images=batch, pages=partial_result)
                logger.debug(
                    f"[task-id {task.id}][model{model.__class__.__name__}][process time {time.time() - t:.2f}]"
                )
            for j, image in enumerate(batch):
                buffer = BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)
                key = f"{task.user_id}/{task.id}/images/page_{i + j}.jpg"
                client_s3.upload_fileobj(buffer, self.file_connector.bucket_name, key)
                logger.debug(f"Uploaded page {i + j} to {key}")
                signed_url = client_s3.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": self.file_connector.bucket_name, "Key": key},
                    ExpiresIn=3600,  # 1h
                )
                partial_result[j].page_url = signed_url

            task.output.pages.extend(partial_result)

            page_range = f"{i + 1}" if len(batch) == 1 else f"{i + 1}-{i + self.batch_size}"
            logger.debug(f"{filename} time to process page {page_range} - {time.time() - t_predict:.2f}s")

            percentage = len(task.output.pages) / task.output.total_pages
            task.output.set_text()
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.IN_PROGRESS.value,
                    percentage=percentage * self.worker_weight + task.percentage,
                    output=task.output,
                    extras=task.extras,
                ),
            )
            logger.debug(task.extras)
        return task

    def set_output(self, task: TaskModel, total_pages: int = -1) -> TaskModel:
        task = self.set_extras(task=task)
        if task.output is None:
            task.output = OCRResult(
                type=self.name,
                model_name=__name__,
                version=__version__,
                created_at=int(time.time()),
                updated_at=int(time.time()),
                total_pages=total_pages,
                pages=[],
            )
        return task

    def _process_task(self, task: TaskModel) -> TaskModel:
        extra_log = {"task_id": task.id, "user_id": task.user_id}
        task = self.set_output(task=task)

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.IN_PROGRESS.value,
                percentage=0,
                extras=task.extras,
                input=task.input,
                output=task.output,
            ),
        )

        filename = task.input.raw_filename
        logger.debug(f"{task.id} - {task.user_id} - {filename} - {task.extras} ", extra=extra_log)
        content = self.get_content_file(task=task)
        content_hash = hash_file(content)
        task.content_hash = content_hash
        logger.debug(f"{task.id} - {content}", extra=extra_log)
        pages = self.transform_content(task=task, content=content)
        logger.debug(f" Start to process - {filename} - {len(pages)}", extra=extra_log)
        if self.cache:
            logger.debug("Search into cache ", extra=extra_log)
            if self.cache.is_in_cache(task=task):
                cache_task = self.cache.get_task_from_cache(task=task)
                logger.debug(
                    f"found into cache with status {cache_task.status} ",
                    extra=extra_log,
                )
                task.output.updated_at = int(time.time())
                task = task_table.update_task(
                    task_id=task.id,
                    form_data=TaskUpdateForm(
                        status=cache_task.status,
                        percentage=cache_task.percentage,
                        extras=cache_task.extras,
                        output=cache_task.output,
                        content_hash=content_hash,
                    ),
                )
                return task

        task.output.total_pages = len(pages)
        task.output.updated_at = int(time.time())
        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.IN_PROGRESS.value,
                percentage=0,
                extras=task.extras,
                output=task.output,
                content_hash=content_hash,
            ),
        )

        try:
            task = self.predict_on_pages(task=task, pages=pages)
        except Exception as e:
            task.extras["error"] = str(e)
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value,
                    percentage=task.percentage,
                    extras=task.extras,
                    content_hash=content_hash,
                ),
            )
            raise

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value,
                percentage=task.percentage,
                extras=task.extras,
                content_hash=content_hash,
            ),
        )
        logger.debug(f"{task.id} - done")

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value,
                percentage=task.percentage,
                extras=task.extras,
                content_hash=content_hash,
            ),
        )

        try:
            self.file_connector.delete_by_task_id(user_id=task.user_id, task_id=task.id)
        except Exception as e:
            logger.warning(str(e))

        return task

    def process_task(self, task: TaskModel) -> TaskModel:
        return self._process_task(task)
