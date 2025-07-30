import os
import json
import time
import traceback


from services.base.pipeline import Pipeline
from src.connector.broker_connector import celery_app, celery_config
from src.logger import logger
from src.schemas.task import TaskForm, TaskModel, TaskStatus, task_table
from .factory import load_worker

process_ocr: Pipeline = load_worker(name=os.environ["PROCESS_NAME"])

logger.info(
    f"{os.environ['WORKER_NAME']} - {os.environ['PROCESS_NAME']} {celery_config.CELERY_APP_NAME}" + "\n" + 79 * "*"
)


@celery_app.task(name=os.environ["WORKER_NAME"], bind=True)
def launch_task(self, task_info: dict):
    task = TaskModel.model_validate(json.loads(task_info))
    try:
        t = time.time()
        logger.info({"task_id": task.id, "message": "Start"})
        task = process_ocr.process(task=task)
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
