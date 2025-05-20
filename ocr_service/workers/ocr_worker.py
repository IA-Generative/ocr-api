import os
import time
from io import BytesIO

from PIL import Image, ImageOps

from ocr_service.configs.paddle import PaddleSetting
from ocr_service.models.base import BaseModelPrediction
from ocr_service.workers.base import BaseWorker
from ocr_service.utils.lazy_pdf import LazyPdfImageList
from src import __name__, __version__
from src.connector.s3_connector import S3Connector
from src.logger import logger
from src.schemas.output import MarkdownPage, OCRResult, Page
from src.schemas.task import TaskModel, TaskStatus, TaskUpdateForm, task_table
from io import BytesIO


class EmptyContentException(Exception): ...


class FileNotSupported(Exception): ...


class OCRWorker(BaseWorker):
    def __init__(
        self,
        file_connector: S3Connector,
        ocr_model: BaseModelPrediction,
        settings: PaddleSetting = PaddleSetting(),
    ):
        self.file_connector = file_connector
        self.ocr_model = ocr_model
        self.settings = settings

    def set_extras(self, task: TaskModel) -> TaskModel:
        task.extras = task.extras if task.extras is not None else {}
        return task

    def get_content_file(self, task: TaskModel) -> str:
        task = self.set_output(task=task)
        try:
            logger.info(f"{task.id} load file ")
            content = self.file_connector.get_by_task_id(
                user_id=task.user_id, task_id=task.id
            )
            logger.info(f"{task.id} loaded")

        except Exception as e:
            task.extras["error"] = str(e)
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value, percentage=0, extras=task.extras
                ),
            )
            logger.error(str(e))
            raise

        if content is None:
            task.extras["error"] = f"No content found for task : {task.id}"
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value, percentage=0, extras=task.extras
                ),
            )
            logger.error(f"No content found for task : {task.id}")
            raise EmptyContentException(f"No content found for task : {task.id}")
        return content

    def transform_content(self, task: TaskModel, content: bytes) -> list[Image.Image] | list[BytesIO]:
        task = self.set_output(task=task)

        content_type: str = task.input.content_type
        logger.debug(f"content-type : {content_type}")
        filename = task.input.raw_filename

        if content_type.startswith("image/"):
            pages = [Image.open(content).convert("RGB")]

        elif content_type == "application/pdf":
            if os.environ.get("MODEL_NAME") != "docling":
                t_convert = time.time()
                logger.debug(f"{task.id} - {filename} convert to image")
                logger.info(79 * "*")

                pages = LazyPdfImageList(content)
                t_convert = time.time() - t_convert
                logger.debug(
                    f"{task.id} - {filename} convert to image nb pages {len(pages)} into {t_convert}"
                )
            else:
                buffer = BytesIO(content.read())
                buffer.seek(0)  # position it back to begin
                pages = [buffer]


        else:
            logger.error(f"Unsupported file type {task.extras}")
            task.extras["error"] = f"Unsupported file type {task.extras}"
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value, percentage=0, extras=task.extras
                ),
            )
            raise FileNotSupported(f"Unsupported file type {content_type}")

        return pages

    def predict_on_pages(self, task: TaskModel, pages: list[Image.Image | BytesIO]) -> TaskModel:
        task = self.set_output(task=task, total_pages=len(pages))
        formatted_result: list[Page] | list[MarkdownPage] = []
        batch_size = self.settings.DETECTION_BATCH_SIZE
        filename = task.extras.get("raw_filename")
        client_s3 = self.file_connector.client
        for i in range(0, len(pages), batch_size):
            t_predict = time.time()
            batch = pages[i : i + batch_size]  # TODO https://docs.python.org/3/library/itertools.html#itertools.batched
            logger.debug(f"{filename=} for task {task.id}")
            # TODO : Pdf with differents size of page

            partial_result: list[Page] | list[MarkdownPage] = self.ocr_model.batch_predict(
                images=batch,
                langs=[["fr"] for _ in batch],
                detection_batch_size=batch_size,
                recognition_batch_size=self.settings.RECOGNITION_BATCH_SIZE,
            )
            for j, image_or_bytes_io in enumerate(batch):
                if isinstance(image_or_bytes_io, Image.Image):
                    assert isinstance(partial_result[j], Page)

                    buffer = BytesIO()
                    image_or_bytes_io.save(buffer, format="JPEG")
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
                else:
                    assert isinstance(partial_result[j], MarkdownPage)

            formatted_result.extend(partial_result)

            page_range = f"{i + 1}" if len(batch) == 1 else f"{i + 1}-{i + batch_size}"
            logger.debug(f"{filename=} time to process page {page_range} - {time.time() - t_predict:.2f}s")
            task.output.pages = formatted_result
            percentage = len(formatted_result) / task.output.total_pages
            task.output.set_text()
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.IN_PROGRESS.value,
                    percentage=percentage,
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
                type="ocr",
                model_name=__name__,
                version=__version__,
                created_at=int(time.time()),
                updated_at=int(time.time()),
                total_pages=total_pages,
                pages=[],
            )
        return task

    def process_task_ocr(self, task: TaskModel) -> TaskModel:
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

        # max_height = task.extras.get("max_height", None)
        # grayscale = task.extras.get("grayscale", False)

        logger.debug(f"{task.id} - {task.user_id} - {filename} - {task.extras} ")

        content = self.get_content_file(task=task)
        logger.debug(f"{task.id} - {content}")
        pages: list[Image.Image] | list[BytesIO] = self.transform_content(task=task, content=content)
        logger.debug(f" Start to process - {filename} - {len(pages)}")

        task.output.total_pages = len(pages)
        task.output.updated_at = int(time.time())
        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.IN_PROGRESS.value,
                percentage=0,
                extras=task.extras,
                output=task.output,
            ),
        )

        # if len(pages) and isinstance(pages[0], Image.Image):
        #     for i, page in enumerate(pages):
        #         width, height = page.size
        #         if max_height and int(height) > max_height:
        #             page = page.resize((int(width * max_height / height), max_height))

        #     if grayscale:
        #         for i in range(len(pages)):
        #             pages[i] = ImageOps.grayscale(pages[i])

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
                ),
            )
            raise

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value,
                percentage=task.percentage,
                extras=task.extras,
            ),
        )
        logger.debug(f"{task.id} - done {task.model_dump()}")

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value,
                percentage=task.percentage,
                extras=task.extras,
            ),
        )

        try:
            self.file_connector.delete_by_task_id(user_id=task.user_id, task_id=task.id)
        except Exception as e:
            logger.warning(str(e))

        return task

    def process_task(self, task: TaskModel) -> TaskModel:
        return self.process_task_ocr(task)
