from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import (
    CeleryTaskName,
    TaskForm,
    TaskOperation,
    TaskStatus,
)
from celery import Task as CeleryTask


from business.chunks.worker import ChunkWorker

from services.utils.validation import validate_task
from services.client.tools import (
    server_client,
)


chunk_worker = ChunkWorker(
    name="chunk-ocr-worker",
    batch_size=1,
    worker_weight=1,
)


class ChunkerWorker(CeleryTask):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed with error: {exc}")
        logger.error(f"Traceback: {einfo.traceback}")

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully.")


@celery_app.task(
    name=CeleryTaskName.OCR_CHUNK_TASK.value,
    bind=True,
    base=ChunkerWorker,
)
def process_ocr_chunk(self: ChunkerWorker, task_info: dict | str) -> dict:
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
                type=CeleryTaskName.OCR_CHUNK_TASK.value,
                group_id=task.group_id,
                status=TaskStatus.STARTED.value,
                percentage=0.0,
                parameters=task.parameters,
                input=task.input,
                output=task.output,
                parent_id=ocr_task_id,
                extras=task.extras,
                content_hash=task.content_hash,
            ).model_dump(exclude_none=True),
        )

    task.id = celery_task_id  # type: ignore

    try:
        result = chunk_worker.process_task(task=task)
        # Update parent OCR task with completed status and classification output
        server_client.update_task_by_id(
            task_id=ocr_task_id,
            task_type=TaskOperation.CHUNK_OCR.value,
            update_data={
                "status": TaskStatus.COMPLETED.value,
                "percentage": 1.0,
                "output": (result.output.model_dump(exclude_none=True) if result.output else None),
            },
        )
        return result.model_dump()
    except Exception as e:
        server_client.update_task_by_id(
            task_id=ocr_task_id,
            task_type=TaskOperation.CHUNK_OCR.value,
            update_data={
                "status": TaskStatus.FAILED.value,
                "extras": {"error": str(e)},
            },
        )
        raise e
