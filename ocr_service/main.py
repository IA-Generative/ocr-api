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
from src.schemas.task import task_table, TaskModel, TaskUpdateForm
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
                form_data=TaskUpdateForm(status="error", percentage=0, extras=extras),
            )
            logger.error(str(e))
            continue

        return_image = extras.get("return_image", False)
        grayscale = extras.get("grayscale", False)
        if content is not None:
            base64_images, formatted_result = [], []
            if ext in [".jpg", ".png"]:
                pages = [Image.open(content).convert("RGB")]

            elif ext == ".pdf":
                t_convert = time.time()
                pages = convert_from_bytes(content.read())
                t_convert = time.time() - t_convert
                logger.debug(
                    f"{filename} convert to image nb pages {len(pages)} into {t_convert}"
                )

            else:
                logger.error(f"Unsupported file type {extras}")
                continue

            logger.debug(f" Start to process - {filename} ")
            extras["nb_pages"] = len(pages)
            task = task_table.update_task(
                task_id=task.id,
                form_data=TaskUpdateForm(
                    status="on-going", percentage=0.1, extras=extras
                ),
            )
            extras = task.extras

            for i, page in enumerate(pages):
                width, height = page.size
                if max_height and int(height) > max_height:
                    page = page.resize((int(width * max_height / height), max_height))
                if return_image:
                    base64_images.append(image_to_base64(page))

                if grayscale:
                    page = ImageOps.grayscale(page)
            n = 2
            for i in range(0, len(pages), n):
                t_predict = time.time()
                batch = pages[i : i + n]

                # Si une seule image restante, empile avec une nouvelle dimension
                if len(batch) == 1:
                    images = np.array(batch[0])
                else:
                    images = np.stack(batch, axis=0)

                logger.debug(images.shape)

                partial_result = perform_ocr_async(images)
                formatted_result.extend(partial_result)

                page_range = f"{i + 1}" if len(batch) == 1 else f"{i + 1}-{i + n}"
                logger.debug(
                    f"{filename} time to process page {page_range} - {time.time() - t_predict:.2f}s"
                )
                percentage = len(formatted_result) / extras.get("nb_pages", 1)
                extras["nb_page_proccesed"] = len(formatted_result)
                task = task_table.update_task(
                    task_id=task.id,
                    form_data=TaskUpdateForm(
                        status="on-going", percentage=percentage, extras=extras
                    ),
                )
                logger.debug(task.extras)
            print(2 * 79 * "*")
            logger.debug(f"{task.id} - done {task.model_dump()}")
            print(2 * 79 * "*")
            task.extras["results"] = formatted_result

            if base64_images:
                task.extras["images_base64"] = base64_images

            redis_client.set(name=f"{task.id}", value=f"{task.model_dump()}", ex=3000)

            try:
                minio_connector.delete_by_task_id(user_id=task.user_id, task_id=task.id)

            except Exception as e:
                logger.error(str(e))
