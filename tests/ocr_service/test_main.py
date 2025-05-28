import boto3
import pytest

from src.schemas.task import task_table, TaskForm, TaskModel, TaskStatus
from src.schemas.input import InputForm
import json

from src.connector.base import BaseFileConnector
from src.connector.s3_connector import S3Connector
from src.config.s3 import S3Settings


@pytest.fixture(scope="module")
def storage_service() -> BaseFileConnector:
    settings = S3Settings()
    return S3Connector(
        s3_client=boto3.client("s3"), bucket_name=settings.S3_BUCKET_NAME
    )


def test_task_process_paddle(storage_service: BaseFileConnector):
    from ocr_service.main import launch_task

    user_id = "test"
    task = task_table.insert_new_task(
        user_id=user_id,
        form_data=TaskForm(
            user_id=user_id,
            type="OCR",
            status=TaskStatus.CREATED.value,
            percentage=0,
            extras={},
        ),
    )

    saved_path = storage_service.save(
        user_id=user_id,
        task_id=task.id,
        file_path="tests/data/valid/cerfa_13750-05-1.pdf",
    )
    task.input = InputForm(
        type="file",
        storage_file_path=saved_path,
        raw_filename="cerfa_13750-05-1.pdf",
        content_type="application/pdf",
        ext=".pdf",
        size=123456,
    )
    result = launch_task.apply(args=(json.dumps(task.model_dump()),))
    result = result.get()
    actual = TaskModel.model_validate(result)
    assert actual.id == task.id
    assert actual.status == TaskStatus.COMPLETED.value
