from src.utils.usage import resource_monitor
from src.logger import logger
from src.schemas.task import TaskModel
from src.connector.minio_connector import MinioConnector
from src.config.minio import MinioSettings
from src.config.redis import RedisSettings
from ocr_service.workers.ocr_worker import OCRWorker
from ocr_service.configs.surya import SuryaSetting
from ocr_service.models.surya_ocr import SuryaOCR
from celery import Celery
import minio
import json

ocr_settings = SuryaSetting()
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
app = Celery(
    'worker', broker=f'redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}/')

ocr_model: SuryaOCR = None
process_ocr: OCRWorker = None


def load_model():
    global ocr_model, process_ocr
    ocr_model = SuryaOCR(checkpoint_detection=ocr_settings.SURYA_DETECTION_FOLDER,
                         checkpoint_recognition=ocr_settings.SURYA_RECOGNITION_FOLDER)
    process_ocr = OCRWorker(minio_connector=minio_connector,
                            ocr_model=ocr_model, settings=ocr_settings)


@app.task(name="worker.tasks.ocr")
# @resource_monitor(interval_sec=5, label='worker.tasks.ocr')
def launch_task(task_info: dict):
    global ocr_model, process_ocr
    if process_ocr is None or ocr_model is None:
        load_model()
    task = TaskModel.model_validate(json.loads(task_info))
    task = process_ocr.process_task(task=task)
    return task.model_dump()


if __name__ == "__main__":
    logger.info("Start to consume...")
    app.start()
