import boto3
import pytest
import json

from unittest.mock import patch

from src.schemas.task import TaskModel, TaskStatus, TaskOperation
from src.schemas.input import InputForm
from services.client.server import ServerClient

from src.connector.base import BaseFileConnector
from src.connector.s3_connector import S3Connector
from src.config.s3 import S3Settings
from src.schemas.output import Page
from services.base.worker import AnyFileProcessWorker
from services.base.pipeline import Pipeline
from services.base.model import BaseModelPrediction
from loguru import logger
import sys

logger.remove()
logger.add(sys.stderr, level="DEBUG")
server_client = ServerClient()


@pytest.fixture(scope="module")
def mocked_models() -> BaseModelPrediction:
    class MockeModel(BaseModelPrediction):
        def batch_predict(self, images, pages=..., *args, **kwargs):
            return [Page(page=i) for i in range(len(images))]

    return MockeModel()


@pytest.fixture(scope="module")
def storage_service() -> BaseFileConnector:
    settings = S3Settings()
    return S3Connector(s3_client=boto3.client("s3"), bucket_name=settings.S3_BUCKET_NAME)


@pytest.fixture(scope="module")
def mocked_pipeline(storage_service: BaseFileConnector, mocked_models: BaseModelPrediction) -> Pipeline:
    return Pipeline([AnyFileProcessWorker(name="mock", file_connector=storage_service, models=[mocked_models])])


def test_task_process_paddle(
    storage_service: BaseFileConnector,
    mocked_pipeline: Pipeline,
):
    with patch("services.factory.load_worker", return_value=mocked_pipeline):
        from services.main import launch_task

        user_id = "test_user"
        task_dict = server_client.create_task(
            task_data=dict(
                type=TaskOperation.OCR.value,
                status=TaskStatus.CREATED.value,
                percentage=0,
                extras={},
                user_id=user_id,
            ),
        )
        task = TaskModel.model_validate(task_dict)

        saved_path = storage_service.save(
            user_id=user_id,
            task_id=task.id,
            file_path="tests/data/valid/cerfa_13750-05-1.pdf",
        )
        task.input = InputForm(
            storage_file_path=saved_path,
            raw_filename="cerfa_13750-05-1.pdf",
            content_type="application/pdf",
            ext=".pdf",
            size=123456,
        )
        logger.debug(f"Task input: {task.input}")
        logger.info(79 * "*")
        result = launch_task.apply(args=(json.dumps(task.model_dump()),))
        result = result.get()
        actual = TaskModel.model_validate(result)
        assert actual.id == task.id
        assert actual.status == TaskStatus.COMPLETED.value
