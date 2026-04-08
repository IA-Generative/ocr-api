import os
import json
import traceback


from services.base.pipeline import Pipeline
from src.connector.broker_connector import celery_app, celery_config
from src.logger import logger
from src.schemas.task import TaskForm, TaskModel, TaskStatus, task_table
from services.base.tracing import get_tracing_service
from .factory import load_worker
from business.chunks.worker import ChunkWorker

process_ocr: Pipeline = load_worker(name=os.environ["PROCESS_NAME"])
non_blocking_chunk_worker = ChunkWorker(name="chunk-worker", batch_size=1, worker_weight=0)

logger.info(
    f"{os.environ['WORKER_NAME']} - {os.environ['PROCESS_NAME']} {celery_config.CELERY_APP_NAME}" + "\n" + 79 * "*"
)

tracing = get_tracing_service(tracing_name=os.environ.get("TRACING_SERVICE", "logging"))


@celery_app.task(name=os.environ["WORKER_NAME"], bind=True)
def launch_task(self, task_info: dict):
    task = TaskModel.model_validate(json.loads(task_info))
    try:
        with tracing.trace_context(trace_id=task.id, user_id=task.user_id, name=os.environ["WORKER_NAME"]):
            task = process_ocr.process(task=task)
            try:
                logger.info(f"Starting non-blocking chunk worker for task {task.id}")
                task = non_blocking_chunk_worker._process_task(task=task)
            except Exception as e:
                logger.error(f"Error in chunk worker: {e}")

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
