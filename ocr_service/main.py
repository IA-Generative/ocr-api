import json
import os
import time
import traceback

import boto3

from ocr_service.clients import get_ocr_processor
from ocr_service.workers.ocr_worker import OCRWorker
from src.connector import S3Connector, s3_settings
from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import TaskForm, TaskModel, TaskStatus, task_table
from src.utils.usage import resource_monitor

s3_client = boto3.client("s3")
s3_client_connector = S3Connector(
    s3_client=s3_client, bucket_name=s3_settings.S3_BUCKET_NAME
)


process_ocr: OCRWorker = get_ocr_processor(file_connector=s3_client_connector)


@celery_app.task(name="worker.tasks.ocr", bind=True)
@resource_monitor(
    interval_sec=int(os.environ.get("MONITOR_RESSOURCE_EVERY", 5)),
    label="worker.tasks.ocr",
)
def launch_task(self, task_info: dict):
    worker_id = self.request.hostname
    task = TaskModel.model_validate(json.loads(task_info))
    try:
        t = time.time()
        logger.info({"task_id": task.id, "worker_id": worker_id, "message": "Start"})
        task = process_ocr.process_task(task=task)
        logger.info(
            {
                "task_id": task.id,
                "process_time": time.time() - t,
                "message": "End",
                "worker_id": worker_id,
            }
        )
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
        raise


if __name__ == "__main__":
    logger.info("Start to consume...")
    celery_app.start()
