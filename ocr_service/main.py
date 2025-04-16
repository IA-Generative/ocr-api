import json

import redis
import minio


from ocr_service.models.surya_ocr import SuryaOCR
from ocr_service.configs.surya import SuryaSetting
from ocr_service.workers.ocr_worker import OCRWorker

from src.config.redis import RedisSettings
from src.config.minio import MinioSettings

from src.connector.minio_connector import MinioConnector
from src.schemas.task import TaskModel
from src.logger import logger

ocr_settings = SuryaSetting()
ocr_model = SuryaOCR(checkpoint_detection=ocr_settings.SURYA_DETECTION_FOLDER,
                     checkpoint_recognition=ocr_settings.SURYA_RECOGNITION_FOLDER)
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


process_ocr = OCRWorker(minio_connector=minio_connector,
                        ocr_model=ocr_model, settings=ocr_settings)
if __name__ == "__main__":
    logger.info("Start to consume")

    while True:
        _, task_in_redis = redis_client.brpop(redis_settings.REDIS_QUEUE_NAME)
        task = TaskModel.model_validate(json.loads(task_in_redis))
        process_ocr.process_task(task=task)
