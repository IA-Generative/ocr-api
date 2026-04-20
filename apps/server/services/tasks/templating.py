from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import (
    CeleryTaskName,
    TaskForm,
    TaskOperation,
    TaskStatus,
)
import time

from celery import Task as CeleryTask
from business.templating.model import TemplatingFieldExtraction
from src.schemas.output import OCRResult
from src.schemas.entity import EntityCreateDefinition
from src.schemas.templating import (
    TemplatingUpdateModel,
    TemplatingExtractionResult,
    EntityZone,
)


from services.utils.validation import validate_task
from services.client.tools import server_client, file_connector

model = TemplatingFieldExtraction()


class TemplatingTask(CeleryTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed with error: {exc}")
        logger.error(f"Traceback: {einfo.traceback}")

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully.")


@celery_app.task(
    name=CeleryTaskName.TEMPLATING_EXTRACTION_TASK.value,
    bind=True,
    base=TemplatingTask,
)
def process_extract_placeholders(self: TemplatingTask, task_info: dict | str) -> dict:
    task = validate_task(task_info)

    # Créer la tâche dans le backend si elle n'existe pas déjà
    try:
        server_client.get_task_by_id(task.id)
    except Exception:
        server_client.create_task(
            TaskForm(
                id=task.id,
                type=CeleryTaskName.TEMPLATING_EXTRACTION_TASK.value,
                group_id=task.group_id,
                status=TaskStatus.STARTED.value,
                percentage=0.0,
                parameters=task.parameters,
                input=task.input,
                output=task.output,
                parent_id=None,
                extras=task.extras,
                content_hash=task.content_hash,
                user_id=task.user_id,
            ).model_dump(exclude_none=True),
        )

    try:
        if task.input is None:
            raise ValueError("Task input cannot be None for templating extraction")

        local_file = file_connector.get_by_task_id(user_id=task.user_id, task_id=task.id)

        valid_fields, invalid_fields = model.process(local_file)
        valid_fields = list(set(valid_fields))
        invalid_fields = list(set(invalid_fields))
        # Update parent OCR task with completed status and classification output
        task_data = server_client.update_task_by_id(
            task_id=task.id,
            task_type=TaskOperation.TEMPLATING_EXTRACTION.value,
            update_data={
                "status": TaskStatus.COMPLETED.value,
                "percentage": 1.0,
                "output": OCRResult(
                    type=TaskOperation.TEMPLATING_EXTRACTION.value,
                    model_name=model.__class__.__name__,
                    version="1.0",
                    total_pages=1,
                    created_at=int(time.time()),
                    updated_at=int(time.time()),
                    pages=[],
                ).model_dump(),
            },
        )
        update_data = TemplatingUpdateModel(
            total_page=1,
            entity_zone=[],
            entity_names=TemplatingExtractionResult(
                valid_fields=valid_fields,
                invalid_fields=invalid_fields,
            ),
        )
        for valid_field in valid_fields:
            logger.info(f"Valid field extracted: {valid_field}")
            entity = EntityCreateDefinition(
                name=valid_field,
            )
            update_data.entity_zone.append(EntityZone(entity_definition=entity, boxes=None))

        server_client.update_templating(
            templating_id=task.id,
            update_data=update_data.model_dump(exclude_unset=True),
        )
        return task_data
    except Exception as e:
        server_client.update_task_by_id(
            task_id=task.id,
            task_type=TaskOperation.TEMPLATING_EXTRACTION.value,
            update_data={
                "status": TaskStatus.FAILED.value,
                "extras": {"error": str(e)},
            },
        )
        raise e
