import boto3
import pytest
from unittest.mock import patch
from src.schemas.task import task_table, TaskForm, TaskModel, TaskOperation, InputForm


from src.connector.base import BaseFileConnector
from src.connector.s3_connector import S3Connector
from src.config.s3 import S3Settings
from business.forms.workers.template import (
    TemplateWorker,
    TemplateWorkerFeature,
    TemplateWorkerSaveTemplate,
    TemplateWorkerQuery,
)


@pytest.fixture
def dummy_task() -> TaskModel:
    return task_table.insert_new_task(user_id="123", form_data=TaskForm(user_id="123", type="ocr", status="created"))


@pytest.fixture(scope="module")
def storage_service() -> BaseFileConnector:
    settings = S3Settings()
    return S3Connector(s3_client=boto3.client("s3"), bucket_name=settings.S3_BUCKET_NAME)


def test_template_worker_is_applicable(
    storage_service: BaseFileConnector,
    dummy_task: TaskModel,
):
    # Initialize the worker
    worker = TemplateWorker(
        name="test_template_worker",
        file_connector=storage_service,  # Mock or provide a real file connector
        models=[],
        batch_size=2,
        worker_weight=1,
        cache=None,
    )
    assert not worker.is_applicable(task=dummy_task)
    dummy_task.type = TaskOperation.SAVE_TEMPLATE
    assert worker.is_applicable(task=dummy_task)


def test_template_worker_feature_is_applicable(
    storage_service: BaseFileConnector,
    dummy_task: TaskModel,
):
    # Initialize the worker
    worker = TemplateWorkerFeature(
        name="test_template_worker_feature",
        file_connector=storage_service,
        models=[],
        batch_size=2,
        worker_weight=1,
        cache=None,
    )
    assert not worker.is_applicable(task=dummy_task)
    dummy_task.type = TaskOperation.VECTORIZE
    assert worker.is_applicable(task=dummy_task)


def test_template_worker_save_template_is_applicable(
    storage_service: BaseFileConnector,
    dummy_task: TaskModel,
):
    # Initialize the worker
    worker = TemplateWorkerSaveTemplate(
        name="test_template_worker_save_template",
        file_connector=storage_service,
        models=[],
        batch_size=2,
        worker_weight=1,
        cache=None,
    )
    assert not worker.is_applicable(task=dummy_task)
    dummy_task.type = TaskOperation.SAVE_TEMPLATE
    dummy_task.input = InputForm(
        content_type="application/pdf",
        storage_file_path="dummy_file_path",
        raw_filename="dummy_file.pdf",
        size=1024,
        ext="pdf",
    )
    with patch.object(worker.file_connector, "get_by_task_id") as mock_get_content_file:
        mock_get_content_file.return_value = "tests/data/valid/cerfa_11573-09-filled.pdf"
        assert worker.is_applicable(task=dummy_task)

        dummy_task.input = InputForm(
            content_type="image/png",
            storage_file_path="dummy_file_path",
            raw_filename="dummy_file.png",
            size=1024,
            ext="png",
        )

        assert worker.is_applicable(task=dummy_task)

        worker.set_output(task=dummy_task, total_pages=3)


def test_template_worker_query_is_applicable(
    storage_service: BaseFileConnector,
    dummy_task: TaskModel,
):
    # Initialize the worker
    worker = TemplateWorkerQuery(
        name="test_template_worker_query",
        file_connector=storage_service,
        models=[],
        batch_size=2,
        worker_weight=1,
        cache=None,
    )
    assert not worker.is_applicable(task=dummy_task)
    dummy_task.type = TaskOperation.FORMS
    assert worker.is_applicable(task=dummy_task)
