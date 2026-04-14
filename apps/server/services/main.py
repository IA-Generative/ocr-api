import os
import json
import traceback
import boto3


from services.base.pipeline import Pipeline
from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import TaskForm, TaskModel, TaskStatus, CeleryTaskName
from services.client.server import ServerClient
from services.base.tracing import get_tracing_service
from .factory import load_worker
from business.chunks.worker import ChunkWorker


from business.classification.models.openai_clip import OpenAIClipModel
from src.connector.s3_connector import S3Connector, s3_settings
from src.schemas.classification import ParameterClassification
from business.classification.worker import ClassificationWorker

s3_client = boto3.client("s3", verify=s3_settings.VERIFY_SSL)


model = OpenAIClipModel()
file_connector = S3Connector(s3_client=s3_client, bucket_name=s3_settings.S3_BUCKET_NAME)
server_client = ServerClient()


process_ocr: Pipeline = load_worker()
non_blocking_chunk_worker = ChunkWorker(name="chunk-worker", batch_size=1, worker_weight=0)
page_classification_worker = ClassificationWorker(
    name="page-classification-worker",
    batch_size=1,
    worker_weight=1,
    models=[model],
    file_connector=file_connector,
    cache=None,
)

tracing = get_tracing_service(tracing_name=os.environ.get("TRACING_SERVICE", "logging"))


def validate_task(task_info: dict | str) -> TaskModel:
    try:
        task_info = task_info if isinstance(task_info, dict) else json.loads(task_info)
        task = TaskModel.model_validate(task_info)
        return task
    except Exception as e:
        logger.error(f"Error validating task: {e}")
        raise ValueError(f"Invalid task data: {e}")


@celery_app.task(name=CeleryTaskName.OCR_TASK.value, bind=True)
def launch_task(self, task_info: dict):
    task = validate_task(task_info)
    with logger.contextualize(task_id=task.id, user_id=task.user_id):
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


@celery_app.task(name=CeleryTaskName.PAGE_CLASSIFICATION_TASK.value, bind=True)
def parocess_page_classification(self, task_info: dict | str) -> dict:
    task = validate_task(task_info)

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


if __name__ == "__main__":
    logger.info("Start to consume...")
    celery_app.start()
