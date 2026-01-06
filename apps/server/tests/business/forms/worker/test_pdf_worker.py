import boto3
import pytest

from src.schemas.task import task_table, TaskForm, TaskModel
from src.schemas.input import InputForm


from src.connector.base import BaseFileConnector
from src.connector.s3_connector import S3Connector
from src.config.s3 import S3Settings
from business.forms.workers.pdf_worker import PDFFormsExtractorWorker


@pytest.fixture
def dummy_task() -> TaskModel:
    return task_table.insert_new_task(user_id="123", form_data=TaskForm(user_id="123", type="ocr", status="created"))


@pytest.fixture(scope="module")
def storage_service() -> BaseFileConnector:
    settings = S3Settings()
    return S3Connector(s3_client=boto3.client("s3"), bucket_name=settings.S3_BUCKET_NAME)


def test_pdf_forms_extractor_worker(
    storage_service: BaseFileConnector,
):
    # Initialize the worker
    worker = PDFFormsExtractorWorker(
        name="test_pdf_worker",
        file_connector=storage_service,  # Mock or provide a real file connector
        models=[],
        batch_size=2,
        worker_weight=1,
        cache=None,
    )

    # Test the worker's initialization
    assert worker.name == "test_pdf_worker"
    assert worker.batch_size == 2
    assert worker.worker_weight == 1

    # Add more tests for specific methods if needed
    # For example, test the predict_on_pages method with mock data


def test_worker_extractor_not_process(
    storage_service: S3Connector,
    dummy_task: TaskModel,
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="tests/data/valid/identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    storage_service.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    worker = PDFFormsExtractorWorker(
        name="test", file_connector=storage_service, models=[], cache=None)
    update_task = worker.process_task(task=dummy_task)
    assert update_task.percentage == dummy_task.percentage
    assert update_task.status != dummy_task.status


def test_worker_extractor_process_pdf(
    storage_service: S3Connector,
    dummy_task: TaskModel,
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/cerfa_11573-09-filled.pdf",
        raw_filename="tests/data/valid/cerfa_11573-09-filled.pdf",
        ext=".pdf",
        size=123456,
        content_type="application/pdf",
    )
    storage_service.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    worker = PDFFormsExtractorWorker(
        name="test", file_connector=storage_service, models=[], cache=None)
    update_task = worker.process_task(task=dummy_task)
    assert update_task != dummy_task
    assert len(update_task.output.pages) > 0
    assert len(update_task.output.pages[1].boxes) > 0
    assert len(update_task.output.pages[1].form_entries) > 0
    assert update_task.output.pages[0].page_url is not None
    assert update_task.output.text is not None
