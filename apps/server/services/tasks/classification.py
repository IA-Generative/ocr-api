import json
import traceback
import boto3
import openai


from services.base.pipeline import Pipeline
from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import (
    TaskForm,
    TaskModel,
    TaskStatus,
    CeleryTaskName,
    TaskOperation,
)
from services.client.server import ServerClient
from celery import Task as CeleryTask

from business.classification.models.text import TextClassificationModel
from src.schemas.classification import ParameterClassification
from business.classification.worker import ClassificationWorker
from src.connector.s3_connector import S3Connector, s3_settings
from src.config.openai import OpenAISettings


openai_settings = OpenAISettings()
file_connector = S3Connector(
    s3_client=boto3.client("s3", verify=s3_settings.VERIFY_SSL),
    bucket_name=s3_settings.S3_BUCKET_NAME,
)


server_client = ServerClient()


model = TextClassificationModel(
    client=openai.OpenAI(api_key=openai_settings.OPENAI_API_KEY, base_url=openai_settings.OPENAI_BASE_URL),
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
    def before_start(self, task_id, args, kwargs):
        logger.info(f"Starting task {task_id} with args: {args} and kwargs: {kwargs}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Task {task_id} failed with error: {exc}")
        logger.error(f"Traceback: {einfo.traceback}")

    def on_success(self, retval, task_id, args, kwargs):
        logger.info(f"Task {task_id} completed successfully.")


def validate_task(task_info: dict | str) -> TaskModel:
    try:
        task_info = task_info if isinstance(task_info, dict) else json.loads(task_info)
        task = TaskModel.model_validate(task_info)
        return task
    except Exception as e:
        logger.error(f"Error validating task: {e}")
        raise ValueError(f"Invalid task data: {e}")


@celery_app.task(name=CeleryTaskName.PAGE_TEXT_CLASSIFICATION_TASK.value, bind=True)
def parocess_text_page_classification(self: ClassificationTask, task_info: dict | str) -> dict:
    task = validate_task(task_info)
    if not model:
        task.extras = task.extras if task.extras else {}
        task.extras["error"] = "Model is not enabled."
        server_client.update_task_by_id(
            task_id=task.id,
            task_type=TaskOperation.PAGE_CLASSIFICATION.value,
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
            task_type=TaskOperation.PAGE_CLASSIFICATION.value,
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
            task_type=TaskOperation.PAGE_CLASSIFICATION.value,
            update_data=TaskForm(
                type=task.type,
                status=TaskStatus.FAILED.value,
                extras=task.extras,
            ).model_dump(exclude_unset=True),
        )
        raise
