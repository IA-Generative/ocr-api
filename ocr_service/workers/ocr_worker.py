from typing import List
from PIL import Image, ImageOps
from pdf2image import convert_from_bytes
import numpy as np

from src.connector.minio_connector import MinioConnector
from src.schemas.task import task_table, TaskModel, TaskUpdateForm, TaskStatus
from src.logger import logger
from src import __version__, __name__

from ocr_service.utils.image import image_to_base64
from ocr_service.models.base import BaseModelPrediction
from ocr_service.configs.surya import SuryaSetting

import time


class EmptyContentException(Exception):
    ...


class OCRWorker:
    def __init__(self, minio_connector: MinioConnector, ocr_model: BaseModelPrediction, settings: SuryaSetting = SuryaSetting()):
        self.minio_connector = minio_connector
        self.ocr_model = ocr_model
        self.settings = settings

    def get_content_file(self, task: TaskModel) -> bytes:
        try:
            content = self.minio_connector.get_by_task_id(
                user_id=task.user_id, task_id=task.id
            )
        except Exception as e:
            task.extras["error"] = str(e)
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value, percentage=0, extras=task.extras),
            )
            logger.error(str(e))
            raise Exception(e)

        if content is None:
            task.extras["error"] = f"No content found for task : {task.id}"
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value, percentage=0, extras=task.extras),
            )
            logger.error(f"No content found for task : {task.id}")
            raise EmptyContentException(
                f"No content found for task : {task.id}")

    def transform_content(self, task: TaskModel, content: bytes) -> List[Image.Image]:
        content_type: str = task.extras.get('content_type', "")
        logger.debug(f'content-type : {content_type}')
        filename = task.extras.get("raw_filename")

        if content_type.startswith("image/"):
            pages = [Image.open(content).convert("RGB")]

        elif content_type == "application/pdf":
            t_convert = time.time()
            pages = convert_from_bytes(content.read())
            t_convert = time.time() - t_convert
            logger.debug(
                f"{task.id} - {filename} convert to image nb pages {len(pages)} into {t_convert}"
            )

        else:
            logger.error(f"Unsupported file type {task.extras}")
            task.extras['error'] = f"Unsupported file type {task.extras}"
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value, percentage=0, extras=task.extras),
            )
            raise Exception(f"Unsupported file type {task.extras}")

        return pages

    def predict_on_pages(self, task: TaskModel, pages: List[Image.Image]) -> TaskModel:
        formatted_result = []
        batch_size = self.settings.SURYA_DETECTION_BATCH_SIZE
        filename = task.extras.get("raw_filename")

        for i in range(0, len(pages), batch_size):
            t_predict = time.time()
            batch = pages[i: i + batch_size]
            for image in batch:
                logger.debug(f"{np.array(image).shape}")
                # TODO : Pdf with differents size of page

            partial_result = self.ocr_model.batch_predict(images=batch, langs=[['fr']for _ in batch],
                                                          detection_batch_size=batch_size,
                                                          recognition_batch_size=self.settings.SURYA_RECOGNITION_BATCH_SIZE)

            formatted_result.extend(partial_result)

            page_range = f"{i + 1}" if len(
                batch) == 1 else f"{i + 1}-{i + batch_size}"
            logger.debug(
                f"{filename} time to process page {page_range} - {time.time() - t_predict:.2f}s"
            )
            percentage = len(formatted_result) / task.extras.get("nb_pages", 1)
            task.extras["nb_page_proccesed"] = len(formatted_result)
            task.extras["results"] = formatted_result

            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.IN_PROGRESS.value, percentage=percentage, extras=task.extras
                ),
            )
            logger.debug(task.extras)
        return task

    def process_task_ocr(self, task: TaskModel) -> TaskModel:
        extras = task.extras if task.extras else {}
        extras["service_name"] = __name__
        extras["version"] = __version__
        filename = extras.get("raw_filename")
        max_height = extras.get("max_height", None)
        return_image = extras.get("return_image", False)
        grayscale = extras.get("grayscale", False)

        base64_images = []
        logger.debug(f"{task.id} - {task.user_id} - {filename} - {extras} ")

        content = self.get_content_file(task=task)
        pages = self.transform_content(task=task, content=content)
        logger.debug(f" Start to process - {filename} ")

        task.extras["nb_pages"] = len(pages)
        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.IN_PROGRESS.value, percentage=0, extras=task.extras
            ),
        )

        for i, page in enumerate(pages):
            width, height = page.size
            if max_height and int(height) > max_height:
                page = page.resize(
                    (int(width * max_height / height), max_height))

        if return_image:
            for page in pages:
                base64_images.append(image_to_base64(page))

        if grayscale:
            for i in range(len(pages)):
                page[i] = ImageOps.grayscale(page[i])

        task = self.predict_on_pages(task=task, pages=pages)

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value, percentage=task.percentage, extras=task.extras
            ),
        )
        logger.debug(f"{task.id} - done {task.model_dump()}")

        if base64_images:
            task.extras["images_base64"] = base64_images

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value, percentage=task.percentage, extras=task.extras
            ),
        )

        try:
            self.minio_connector.delete_by_task_id(
                user_id=task.user_id, task_id=task.id)
        except Exception as e:
            logger.warning(str(e))

        return task
