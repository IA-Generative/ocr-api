import os
import pytest

from src.schemas.task import TaskForm, TaskModel, task_table, TaskStatus
from src.schemas.input import InputForm
from src.logger import logger
from services.factory import load_worker, s3_client_connector


@pytest.fixture
def dummy_task() -> TaskModel:
    return task_table.insert_new_task(user_id="123", form_data=TaskForm(user_id="123", type="ocr", status="created"))


@pytest.mark.skipif(os.environ["PROCESS_NAME"] != "paddleocr-2.10.0", reason="Is not paddleocr-2.10.0")
def test_load_worker_paddleocr2_integration(dummy_task: TaskModel):
    dummy_task.input = InputForm(
        type="file",
        storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
        raw_filename="cerfa_13750-05-1.pdf",
        content_type="application/pdf",
        ext=".pdf",
        size=123456,
    )
    saved_path = s3_client_connector.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path="tests/data/valid/cerfa_13750-05-1.pdf",
    )
    dummy_task.input.storage_file_path = saved_path
    logger.info(saved_path)
    logger.info(79 * "*")
    worker = load_worker(name="paddleocr-2.10.0")
    task = worker.process_task(task=dummy_task)
    assert task.percentage == 1
    assert task.status == TaskStatus.COMPLETED.value
