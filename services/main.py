import json
import time
import traceback

from services.base.worker import BaseWorker
from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import TaskForm, TaskModel, TaskStatus, task_table
from .factory import load_worker, worker_name

process_ocr: BaseWorker = load_worker(name=worker_name)


@celery_app.task(name=worker_name, bind=True)
def launch_task(self, task_info: dict):
    task = TaskModel.model_validate(json.loads(task_info))
    try:
        t = time.time()
        logger.info({"task_id": task.id, "message": "Start"})
        task = process_ocr.process_task(task=task)
        logger.info({"task_id": task.id, "process_time": time.time() - t, "message": "End"})
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
