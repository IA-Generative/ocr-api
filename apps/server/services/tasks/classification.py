from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import (
    CeleryTaskName,
    TaskForm,
    TaskStatus,
)
from celery import Task as CeleryTask


from business.classification.models.text import TextClassificationModel
from business.classification.worker import ClassificationWorker

from services.utils.validation import validate_task
from services.client.tools import (
    openai_client,
    file_connector,
    openai_settings,
    server_client,
)


model = TextClassificationModel(
    client=openai_client,
    model_name=openai_settings.OPENAI_MODEL,
)

page_classification_worker = ClassificationWorker(
    name="page-text-classification-worker",
    batch_size=1,
    worker_weight=1,
    models=[model],
    file_connector=file_connector,
    cache=None,
)


class ClassificationTask(CeleryTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed with error: {exc}")
        logger.error(f"Traceback: {einfo.traceback}")

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully.")


@celery_app.task(
    name=CeleryTaskName.PAGE_TEXT_CLASSIFICATION_TASK.value,
    bind=True,
    base=ClassificationTask,
)
def process_text_page_classification(self: ClassificationTask, task_info: dict | str) -> dict:
    task = validate_task(task_info)
    celery_task_id = self.request.id
    ocr_task_id = task.id  # L'ID de la tâche OCR parente

    # Créer la tâche dans le backend si elle n'existe pas déjà
    try:
        server_client.get_task_by_id(celery_task_id)
    except Exception:
        server_client.create_task(
            TaskForm(
                id=celery_task_id,
                type=CeleryTaskName.PAGE_TEXT_CLASSIFICATION_TASK.value,
                group_id=task.group_id,
                status=TaskStatus.STARTED.value,
                percentage=0.0,
                parameters=task.parameters,
                input=task.input,
                parent_id=ocr_task_id,
            ).model_dump(exclude_none=True),
        )

    task.id = celery_task_id  # type: ignore

    try:
        return model.process(task=task).model_dump()
    except Exception as e:
        raise e
