import time
import json

from PIL import Image, ImageOps
import numpy as np
from pdf2image import convert_from_bytes
import redis
import minio

from ocr_service.models.paddle import perform_ocr_async
from src import __name__ as name, __version__
from ocr_service.utils.image import image_to_base64
from src.config.redis import RedisSettings
from src.config.minio import MinioSettings

from src.connector.minio_connector import MinioConnector
from src.schemas.task import task_table, TaskModel, TaskUpdateForm, TaskStatus
from src.logger import logger


if __name__ == "__main__":
    minio_settings = MinioSettings()
    minio_client = minio.Minio(
        endpoint=minio_settings.MINIO_END_POINT,
        access_key=minio_settings.MINIO_ACCESS_KEY,
        secret_key=minio_settings.MINIO_SECRET_KEY,
        secure=False,
    )
    minio_connector = MinioConnector(
        minio_client=minio_client, bucket_name=minio_settings.MINIO_BUCKET_NAME
    )

    redis_settings = RedisSettings()
    redis_client = redis.Redis(
        host=redis_settings.REDIS_HOST, port=redis_settings.REDIS_PORT, db=0
    )
    logger.info("Start to consume")
    while True:
        _, task_in_redis = redis_client.brpop(redis_settings.REDIS_QUEUE_NAME)
        task = TaskModel.model_validate(json.loads(task_in_redis))

        extras = task.extras if task.extras else {}
        extras["service_name"] = name
        extras["version"] = __version__
        ext = extras.get("ext")
        filename = extras.get("raw_filename")
        max_height = extras.get("max_height", None)
        content_type: str = extras.get('content_type', "")
        return_image = extras.get("return_image", False)
        grayscale = extras.get("grayscale", False)
        batch_size = 2

        base64_images, formatted_result = [], []
        logger.debug(f"{task.id} - {task.user_id} - {filename} - {extras} ")

        t = time.time()
        try:
            content = minio_connector.get_by_task_id(
                user_id=task.user_id, task_id=task.id
            )
        except Exception as e:
            extras["error"] = str(e)
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value, percentage=0, extras=extras),
            )
            logger.error(str(e))
            continue

        if content is None:
            extras["error"] = f"No content found for task : {task.id}"
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value, percentage=0, extras=extras),
            )
            logger.error(f"No content found for task : {task.id}")
            continue

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
            logger.error(f"Unsupported file type {extras}")
            extras['error'] = f"Unsupported file type {extras}"
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.FAILED.value, percentage=0, extras=extras),
            )
            continue

        logger.debug(f" Start to process - {filename} ")
        extras["nb_pages"] = len(pages)
        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.IN_PROGRESS.value, percentage=0, extras=extras
            ),
        )
        task.extras = task.extras if task.extras else {}

        for i, page in enumerate(pages):
            width, height = page.size
            if max_height and int(height) > max_height:
                page = page.resize(
                    (int(width * max_height / height), max_height))
            if return_image:
                base64_images.append(image_to_base64(page))

            if grayscale:
                page = ImageOps.grayscale(page)

        for i in range(0, len(pages), batch_size):
            t_predict = time.time()
            batch = pages[i: i + batch_size]
            for image in batch:
                logger.debug(f"{np.array(image).shape}")
                # TODO : Pdf with differents size of page

            # Si une seule image restante, empile avec une nouvelle dimension
            if len(batch) == 1:
                images = np.array(batch[0])
            else:
                images = np.stack(batch, axis=0)

            logger.debug(images.shape)

            partial_result = perform_ocr_async(images)
            formatted_result.extend(partial_result)

            page_range = f"{i + 1}" if len(
                batch) == 1 else f"{i + 1}-{i + batch_size}"
            logger.debug(
                f"{filename} time to process page {page_range} - {time.time() - t_predict:.2f}s"
            )
            percentage = len(formatted_result) / extras.get("nb_pages", 1)
            task.extras["nb_page_proccesed"] = len(formatted_result)
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status=TaskStatus.IN_PROGRESS.value, percentage=percentage, extras=task.extras
                ),
            )
            logger.debug(task.extras)

        task.extras["results"] = formatted_result

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value, percentage=percentage, extras=task.extras
            ),
        )
        logger.debug(f"{task.id} - done {task.model_dump()}")

        if base64_images:
            task.extras["images_base64"] = base64_images

        redis_client.set(name=f"{task.id}",
                         value=json.dumps(task.model_dump()), ex=3000)

        task = task_table.update_task(
            task_id=task.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.COMPLETED.value, percentage=percentage, extras=task.extras
            ),
        )

        try:
            minio_connector.delete_by_task_id(
                user_id=task.user_id, task_id=task.id)
        except Exception as e:
            logger.error(str(e))
