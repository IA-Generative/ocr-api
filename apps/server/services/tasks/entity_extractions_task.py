from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import (
    CeleryTaskName,
    TaskForm,
    TaskOperation,
    TaskStatus,
)
from celery import Task as CeleryTask


from business.entities.models.llm import TextEntityExtractionModel
from src.schemas.entity import EntityExtractionResult

from services.utils.validation import validate_task
from services.client.tools import (
    server_client,
)


model = TextEntityExtractionModel()


class EntityExtractionTask(CeleryTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed with error: {exc}")
        logger.error(f"Traceback: {einfo.traceback}")

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully.")


@celery_app.task(
    name=CeleryTaskName.ENTITY_EXTRACTION_TASK.value,
    bind=True,
    base=EntityExtractionTask,
)
def process_entity_extraction(self: EntityExtractionTask, task_info: dict | str) -> dict:
    task = validate_task(task_info)
    celery_task_id = self.request.id
    chunk_task_id = task.id  # ID de la tâche OCR_CHUNK (parent direct)

    # Créer la tâche dans le backend si elle n'existe pas déjà
    try:
        server_client.get_task_by_id(celery_task_id)
    except Exception:
        server_client.create_task(
            TaskForm(
                id=celery_task_id,
                type=CeleryTaskName.ENTITY_EXTRACTION_TASK.value,
                group_id=task.group_id,
                status=TaskStatus.STARTED.value,
                percentage=0.0,
                parameters=task.parameters,
                input=task.input,
                output=task.output,
                parent_id=chunk_task_id,
                extras=task.extras,
                content_hash=task.content_hash,
                user_id=task.user_id,
            ).model_dump(exclude_none=True),
        )

    task.id = celery_task_id

    try:
        result: EntityExtractionResult = model.process(task=task)
        if not task.output:
            raise ValueError("Task output is required for entity extraction")

        task.output.entities = result.entities

        server_client.update_task_by_id(
            task_id=celery_task_id,
            task_type=TaskOperation.ENTITY_EXTRACTION.value,
            update_data={
                "status": TaskStatus.COMPLETED.value,
                "percentage": 0.99,
                "output": {
                    **(task.output.model_dump(exclude_none=True) if task.output else {}),
                    "entities": [e.model_dump(exclude_none=True) for e in result.entities],
                },
            },
        )
        return task.model_dump(exclude_none=True)
    except Exception as e:
        server_client.update_task_by_id(
            task_id=celery_task_id,
            task_type=TaskOperation.ENTITY_EXTRACTION.value,
            update_data={
                "status": TaskStatus.FAILED.value,
                "extras": {"error": str(e)},
            },
        )
        raise e
