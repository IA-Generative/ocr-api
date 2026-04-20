from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import (
    CeleryTaskName,
    TaskForm,
    TaskOperation,
    TaskStatus,
)

from celery import Task as CeleryTask
from business.templating.filling_template import FillingTemplate

from src.schemas.templating import TemplatingModel


from services.utils.validation import validate_task
from services.client.tools import server_client, file_connector

model = FillingTemplate()


class TemplatingFillingTask(CeleryTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed with error: {exc}")
        logger.error(f"Traceback: {einfo.traceback}")

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully.")


@celery_app.task(
    name=CeleryTaskName.TEMPLATING_FILLING_TASK.value,
    bind=True,
    base=TemplatingFillingTask,
)
def process_fill_template(self: TemplatingFillingTask, task_info: dict | str) -> dict:
    task = validate_task(task_info)
    parent_task_id = task.id  # ID de la tâche d'extraction de template (parent direct)
    celery_task_id = self.request.id

    # Créer la tâche dans le backend si elle n'existe pas déjà
    try:
        server_client.get_task_by_id(celery_task_id)
    except Exception:
        server_client.create_task(
            TaskForm(
                id=celery_task_id,
                type=CeleryTaskName.TEMPLATING_FILLING_TASK.value,
                group_id=task.group_id,
                status=TaskStatus.STARTED.value,
                percentage=0.0,
                parameters=task.parameters,
                input=task.input,
                output=task.output,
                parent_id=parent_task_id,
                extras=task.extras,
                content_hash=task.content_hash,
                user_id=task.user_id,
            ).model_dump(exclude_none=True),
        )

    try:
        if task.input is None:
            raise ValueError("Task input cannot be None for templating filling")
        if task.parameters is None or task.parameters.get("template_id") is None:
            raise ValueError("Template ID cannot be None for templating filling")
        if task.output is None or task.output.entities is None:
            raise ValueError("OCR output with pages is required for templating filling")

        template_id = task.parameters["template_id"]

        template = server_client.get_templating_by_id(template_id)

        template_model: TemplatingModel = TemplatingModel.model_validate(template)
        template_path = file_connector.get_by_task_id(user_id=task.user_id, task_id=template_model.id)

        entity_definitions = {e.entity_name: e.value for e in task.output.entities}

        output_path = model.process(template_path, entity_definitions)

        strage_output_path = file_connector.save(user_id=task.user_id, task_id=celery_task_id, file_path=output_path)
        task.output.result_path = strage_output_path

        # Update parent OCR task with completed status and classification output
        task_data = server_client.update_task_by_id(
            task_id=celery_task_id,
            task_type=TaskOperation.TEMPLATING_FILLING.value,
            update_data={
                "status": TaskStatus.COMPLETED.value,
                "percentage": 1.0,
                "output": task.output.model_dump(),
            },
        )

        return task_data
    except Exception as e:
        server_client.update_task_by_id(
            task_id=celery_task_id,
            task_type=TaskOperation.TEMPLATING_FILLING.value,
            update_data={
                "status": TaskStatus.FAILED.value,
                "extras": {"error": str(e)},
            },
        )
        raise e
