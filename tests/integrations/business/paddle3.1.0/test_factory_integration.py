import os
import pytest

from src.schemas.task import TaskForm, TaskModel, task_table, TaskStatus
from src.schemas.input import InputForm
from src.logger import logger
from services.factory import load_worker, s3_client_connector


@pytest.fixture
def dummy_task() -> TaskModel:
    return task_table.insert_new_task(user_id="123", form_data=TaskForm(user_id="123", type="ocr", status="created"))


pipelines = ["paddleocr-3.0.1-pipeline", "paddleocr-3.0.1", "mixed-classic-and-vlm"]


@pytest.mark.skipif(os.environ["PROCESS_NAME"] not in pipelines, reason=f"Is not in {pipelines}")
def test_load_worker_paddleocr3_integration(dummy_task: TaskModel):
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
    worker = load_worker(name="paddleocr-3.0.1")
    task = worker.process_task(task=dummy_task)
    assert task.percentage == 1
    assert task.status == TaskStatus.COMPLETED.value


@pytest.mark.skipif(os.environ["PROCESS_NAME"] not in pipelines, reason=f"Is not in {pipelines}")
def test_load_worker_paddleocr3_pipeline_integration(dummy_task: TaskModel):
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
    worker = load_worker(name="paddleocr-3.0.1-pipeline")
    task = worker.process_task(task=dummy_task)
    assert task.percentage == 1
    assert task.status == TaskStatus.COMPLETED.value


is_llm_set = all(
    [
        os.environ.get("OPENAI_BASE_URL"),
        os.environ.get("OPENAI_API_KEY"),
        os.environ.get("INSTRUCT_MODEL_NAME"),
    ]
)


@pytest.mark.skipif(os.environ["PROCESS_NAME"] not in pipelines, reason=f"Is not in {pipelines}")
@pytest.mark.skipif(condition=not is_llm_set, reason="LLM not set")
def test_load_worker_paddleocr3_pipeline_mixed_integration(dummy_task: TaskModel):
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
    worker = load_worker(name="mixed-classic-and-vlm")
    task = worker.process_task(task=dummy_task)
    assert task.percentage == 1
    assert task.status == TaskStatus.COMPLETED.value
