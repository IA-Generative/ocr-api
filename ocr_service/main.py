import json
import traceback
import os
from src.utils.usage import resource_monitor
from src.logger import logger
from src.schemas.task import TaskModel, task_table, TaskForm, TaskStatus
from src.connector.minio_connector import MinioConnector
from src.config.minio import MinioSettings
from src.config.redis import RedisSettings
from ocr_service.workers.ocr_worker import OCRWorker

from celery import Celery
import minio
AVAILABLE_MODEL = ["paddle", "surya"]

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
    "worker", broker=f"redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}/"
)
model_name = os.environ.get('MODEL_NAME', "paddle")
if model_name == "surya":
    from ocr_service.configs.surya import SuryaSetting
    from ocr_service.models.surya_ocr import SuryaOCR
    ocr_settings = SuryaSetting()
    ocr_model = SuryaOCR(
        checkpoint_detection=ocr_settings.SURYA_DETECTION_FOLDER,
        checkpoint_recognition=ocr_settings.SURYA_RECOGNITION_FOLDER,
    )

elif model_name == "paddle":
    from ocr_service.configs.paddle import PaddleSetting
    from ocr_service.models.surya_ocr import SuryaOCR
    ocr_settings = PaddleSetting()
    ocr_model = SuryaOCR(
        checkpoint_detection=ocr_settings.SURYA_DETECTION_FOLDER,
        checkpoint_recognition=ocr_settings.SURYA_RECOGNITION_FOLDER,
    )

else:
    raise NotImplementedError(f'{args.model} is not available yet ({AVAILABLE_MODEL})')
process_ocr = OCRWorker(
    minio_connector=minio_connector, ocr_model=ocr_model, settings=ocr_settings
)


@app.task(name="worker.tasks.ocr")
@resource_monitor(
    interval_sec=os.environ.get("MONITOR_RESSOURCE_EVERY", 5), label="worker.tasks.ocr"
)
def launch_task(task_info: dict):
    task = TaskModel.model_validate(json.loads(task_info))
    try:
        task = process_ocr.process_task(task=task)
        return task.model_dump()
    except Exception as e:
        task.extras = task.extras if task.extras else {}
        task.extras["error"] = str(e)
        task.extras["traceback"] = traceback.format_exc()
        task_table.update_task(
            task_id=task.id,
            form_data=TaskForm(
                user_id=task.user_id,
                type=task.type,
                status=TaskStatus.FAILED.value,
                extras=task.extras,
            ),
        )


if __name__ == "__main__":
    logger.info("Start to consume...")
    app.start()
