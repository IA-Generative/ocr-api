import boto3
import pytest

from src.schemas.task import task_table, TaskForm, TaskModel
from src.schemas.input import InputForm
from src.connector.base import BaseFileConnector
from src.connector.s3_connector import S3Connector
from src.config.s3 import S3Settings


from business.extractions.worker.file_worker import (
    CSVWorker,
    DocxWorker,
    XlsxWorker,
    OdtWorker,
    OdsWorker,
    OdpWorker,
)


@pytest.fixture
def dummy_task() -> TaskModel:
    return task_table.insert_new_task(user_id="123", form_data=TaskForm(user_id="123", type="ocr", status="created"))


@pytest.fixture(scope="module")
def storage_service() -> BaseFileConnector:
    settings = S3Settings()
    return S3Connector(s3_client=boto3.client("s3"), bucket_name=settings.AWS_BUCKET_NAME)


def test_csv_worker_creation(storage_service: BaseFileConnector, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/test.csv",
        raw_filename="tests/data/valid/test.csv",
        ext=".csv",
        size=123456,
        content_type="text/csv",
    )
    key = storage_service.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    dummy_task.input.storage_file_path = key
    worker = CSVWorker(name="test", file_connector=storage_service, cache=None)
    update_task = worker.process_task(task=dummy_task)
    assert update_task.percentage == 1
    assert update_task.status != dummy_task.status


def test_docx_worker_creation(storage_service: BaseFileConnector, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/file-sample_500kB.docx",
        raw_filename="file-sample_500kB.docx",
        ext=".docx",
        size=512000,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    key = storage_service.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    dummy_task.input.storage_file_path = key
    worker = DocxWorker(name="test", file_connector=storage_service, cache=None)
    update_task = worker.process_task(task=dummy_task)
    assert update_task.percentage == 1
    assert update_task.status != dummy_task.status


def test_xlsx_worker_creation(storage_service: BaseFileConnector, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/file_example_XLSX_10.xlsx",
        raw_filename="file_example_XLSX_10.xlsx",
        ext=".xlsx",
        size=10240,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    key = storage_service.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    dummy_task.input.storage_file_path = key

    worker = XlsxWorker(name="test", file_connector=storage_service, cache=None)
    update_task = worker.process_task(task=dummy_task)
    assert update_task.percentage == 1
    assert update_task.status != dummy_task.status


def test_odt_worker_creation(storage_service: BaseFileConnector, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/file-sample_100kB.odt",
        raw_filename="file-sample_100kB.odt",
        ext=".odt",
        size=102400,
        content_type="application/vnd.oasis.opendocument.text",
    )
    key = storage_service.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    dummy_task.input.storage_file_path = key
    worker = OdtWorker(name="test", file_connector=storage_service, cache=None)
    update_task = worker.process_task(task=dummy_task)
    assert update_task.percentage == 1
    assert update_task.status != dummy_task.status


def test_ods_worker_creation(storage_service: BaseFileConnector, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/file_example_ODS_10.ods",
        raw_filename="file_example_ODS_10.ods",
        ext=".ods",
        size=10240,
        content_type="application/vnd.oasis.opendocument.spreadsheet",
    )
    key = storage_service.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    dummy_task.input.storage_file_path = key
    worker = OdsWorker(name="test", file_connector=storage_service, cache=None)
    update_task = worker.process_task(task=dummy_task)
    assert update_task.percentage == 1
    assert update_task.status != dummy_task.status


def test_odp_worker_creation(storage_service: BaseFileConnector, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/file_example_ODP_200kB.odp",
        raw_filename="file_example_ODP_200kB.odp",
        ext=".odp",
        size=204800,
        content_type="application/vnd.oasis.opendocument.presentation",
    )
    key = storage_service.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    dummy_task.input.storage_file_path = key
    worker = OdpWorker(name="test", file_connector=storage_service, cache=None)
    update_task = worker.process_task(task=dummy_task)
    assert update_task.percentage == 1
    assert update_task.status != dummy_task.status
