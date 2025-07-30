import os
import pytest

from src.schemas.task import TaskForm, TaskModel, task_table, TaskStatus
from src.schemas.output import FormEntry
from src.schemas.input import InputForm
from services.factory import load_worker, s3_client_connector


@pytest.fixture(scope="function")
def dummy_task() -> TaskModel:
    return task_table.insert_new_task(user_id="123", form_data=TaskForm(user_id="123", type="ocr", status="created"))


@pytest.mark.skipif(os.environ["PROCESS_NAME"] != "paddleocr-2.10.0", reason="Is not paddleocr-2.10.0")
def test_load_worker_paddleocr2_integration(dummy_task: TaskModel):
    dummy_task.input = InputForm(
        type="file",
        storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
        raw_filename="tests/data/valid/cerfa_13750-05-1.pdf",
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
    worker = load_worker(name="paddleocr-2.10.0")
    task = worker.process(task=dummy_task)
    assert task.percentage == 1
    assert task.status == TaskStatus.COMPLETED.value


@pytest.mark.skipif(os.environ["PROCESS_NAME"] != "paddleocr-2.10.0", reason="Is not paddleocr-2.10.0")
def test_load_worker_paddleocr2_with_form_integration(dummy_task: TaskModel):
    dummy_task.input = InputForm(
        type="file",
        storage_file_path="tests/data/valid/cerfa_11573-09-filled.pdf",
        raw_filename="tests/data/valid/cerfa_11573-09-filled.pdf",
        content_type="application/pdf",
        ext=".pdf",
        size=123456,
    )
    saved_path = s3_client_connector.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path="tests/data/valid/cerfa_11573-09-filled.pdf",
    )
    dummy_task.input.storage_file_path = saved_path

    worker = load_worker(name="paddleocr-2.10.0")
    task = worker.process(task=dummy_task)
    assert task.percentage == 1
    assert task.status == TaskStatus.COMPLETED.value
    assert len(task.output.pages[1].form_entries) > 0
    assert len(task.output.pages[1].boxes) > 0

    assert isinstance(task.output.pages[1].form_entries[0], FormEntry)


@pytest.mark.skipif(os.environ["PROCESS_NAME"] != "paddleocr-2.10.0", reason="Is not paddleocr-2.10.0")
def test_load_worker_paddleocr2_png_integration(dummy_task: TaskModel):
    #### From png image test
    dummy_task.input = InputForm(
        type="file",
        storage_file_path="tests/data/valid/formule.png",
        raw_filename="tests/data/valid/formule.png",
        content_type="image/png",
        ext=".png",
        size=123456,
    )
    saved_path = s3_client_connector.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path="tests/data/valid/formule.png",
    )
    dummy_task.input.storage_file_path = saved_path

    worker = load_worker(name="paddleocr-2.10.0")
    task = worker.process(task=dummy_task)

    assert task.percentage == 1
    assert task.status == TaskStatus.COMPLETED.value
    assert len(task.output.pages[0].form_entries) == 0
    assert len(task.output.pages[0].boxes) > 0
