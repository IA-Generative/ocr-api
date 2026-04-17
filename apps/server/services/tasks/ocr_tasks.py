import traceback


from services.base.pipeline import Pipeline
from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import TaskForm, TaskStatus, CeleryTaskName
from celery import Task as CeleryTask

from ..factory import load_worker


from services.utils.validation import validate_task
from services.client.tools import server_client


process_ocr: Pipeline = load_worker()


class OcrTask(CeleryTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed with error: {exc}")
        logger.error(f"Traceback: {einfo.traceback}")


@celery_app.task(name=CeleryTaskName.OCR_TASK.value, bind=True, base=OcrTask)
def launch_task(self: OcrTask, task_info: dict):
    task = validate_task(task_info)
    with logger.contextualize(  # ty:ignore[unresolved-attribute]
        task_id=task.id, user_id=task.user_id
    ):
        try:
            task = process_ocr.process(task=task)
            logger.debug(79 * "-")
            return task.model_dump()
        except Exception as e:
            task.extras = task.extras if task.extras else {}
            task.extras["error"] = str(e)
            task.extras["traceback"] = traceback.format_exc()
            server_client.update_task_by_id(
                task_id=task.id,
                task_type=task.type,
                update_data=TaskForm(
                    type=task.type,
                    status=TaskStatus.FAILED.value,
                    extras=task.extras,
                ).model_dump(exclude_unset=True),
            )
            raise
