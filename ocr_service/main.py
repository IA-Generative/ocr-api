import json
import traceback
import os
import time
from src.utils.usage import resource_monitor
from src.logger import logger
from src.schemas.task import TaskModel, task_table, TaskForm, TaskStatus
from src.config.redis import RedisSettings
from ocr_service.workers.ocr_worker import OCRWorker
from ocr_service.clients import get_ocr_processor
from celery import Celery


redis_settings = RedisSettings()
app = Celery(
    "worker", broker=f"redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}/"
)
process_ocr: OCRWorker = get_ocr_processor()


@app.task(name="worker.tasks.ocr", bind=True)
@resource_monitor(
    interval_sec=os.environ.get("MONITOR_RESSOURCE_EVERY", 5), label="worker.tasks.ocr"
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
    app.start()
