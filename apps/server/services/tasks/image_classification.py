import traceback


from services.base.pipeline import Pipeline
from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import TaskForm, TaskStatus, CeleryTaskName
from business.chunks.worker import ChunkWorker


from business.classification.models.openai_clip import OpenAIClipModel
from src.schemas.classification import ParameterClassification
from business.paddleocr2.configs.classification import ClassificationSettings
from business.classification.worker import ClassificationWorker
from services.utils.validation import validate_task
from services.client.tools import (
    file_connector,
    server_client,
)


classification_settings = ClassificationSettings()
model = None
if classification_settings.ENABLED:
    model = OpenAIClipModel(
        model_name=classification_settings.MODEL_NAME,
        download_root=classification_settings.CLIP_MODEL_DIR,
    )


non_blocking_chunk_worker = ChunkWorker(name="chunk-worker", batch_size=1, worker_weight=0)
page_classification_worker = ClassificationWorker(
    name="page-classification-worker",
    batch_size=1,
    worker_weight=1,
    models=[model] if model else [],
    file_connector=file_connector,
    cache=None,
)


@celery_app.task(name=CeleryTaskName.PAGE_CLASSIFICATION_TASK.value, bind=True)
def parocess_page_classification(self, task_info: dict | str) -> dict:
    task = validate_task(task_info)
    task.id = self.request.id  # type: ignore
    if not model:
        task.extras = task.extras if task.extras else {}
        task.extras["error"] = "Model is not enabled."
        server_client.update_task_by_id(
            task_id=task.id,
            task_type=task.type,
            update_data=TaskForm(
                type=task.type,
                status=TaskStatus.FAILED.value,
                extras=task.extras,
            ).model_dump(exclude_unset=True),
        )
        raise ValueError("Model is not enabled.")

    try:
        if not task.parameters:
            raise ValueError("Task parameters are required for classification.")
        parameters = ParameterClassification.model_validate(task.parameters)

        if parameters.labels:
            model.set_labels(parameters.labels)
        else:
            logger.warning(f"Task {task.id} - No labels provided for classification. Skipping classification step.")
            raise ValueError("No labels provided for classification.")
    except Exception as e:
        task.extras = task.extras if task.extras else {}
        task.extras["error"] = f"Invalid parameters: {e}"
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
    if model:
        page_classification_worker.models[0] = model
    process_pipeline: Pipeline = Pipeline(workers=[page_classification_worker])
    try:
        task = process_pipeline.process(task=task)
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
