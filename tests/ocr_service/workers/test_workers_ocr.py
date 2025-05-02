from unittest.mock import MagicMock

import pytest
from PIL import Image

from ocr_service.configs.paddle import PaddleSetting
from ocr_service.models.paddle_ocr import PaddleInferOCR
from ocr_service.workers.ocr_worker import EmptyContentException, FileNotSupported, OCRWorker
from src.schemas.input import InputForm
from src.schemas.task import TaskForm, TaskModel, TaskStatus, task_table

settings = PaddleSetting()


@pytest.fixture
def dummy_task() -> TaskModel:
    return task_table.insert_new_task(user_id="123", form_data=TaskForm(user_id="123", type="ocr", status="created"))


@pytest.fixture
def mock_minio():
    return MagicMock()


@pytest.fixture
def mock_model() -> PaddleInferOCR:
    return PaddleInferOCR(path_model=settings.PADDLE_OCR_BASE_DIR)


def test_get_content_file_success(mock_minio, mock_model: PaddleInferOCR, dummy_task: TaskModel):
    expected_content = b"fake-bytes-content"
    mock_minio.get_by_task_id.return_value = expected_content

    worker = OCRWorker(file_connector=mock_minio, ocr_model=mock_model)
    content = worker.get_content_file(task=dummy_task)

    assert content == expected_content
    mock_minio.get_by_task_id.assert_called_once_with(user_id=dummy_task.user_id, task_id=dummy_task.id)


def test_get_content_file_none(mock_minio, mock_model: PaddleInferOCR, dummy_task: TaskModel):
    mock_minio.get_by_task_id.return_value = None

    worker = OCRWorker(file_connector=mock_minio, ocr_model=mock_model)

    with pytest.raises(EmptyContentException):
        worker.get_content_file(task=dummy_task)

    mock_minio.get_by_task_id.assert_called_once()


def test_get_content_file_exception(mock_minio, mock_model: PaddleInferOCR, dummy_task: TaskModel):
    mock_minio.get_by_task_id.side_effect = Exception("Connection error")

    worker = OCRWorker(file_connector=mock_minio, ocr_model=mock_model)

    with pytest.raises(Exception) as exc_info:
        worker.get_content_file(task=dummy_task)

    assert "Connection error" in str(exc_info.value)
    mock_minio.get_by_task_id.assert_called_once()


def test_set_task_extras(mock_minio, mock_model: PaddleInferOCR, dummy_task: TaskModel):
    worker = OCRWorker(file_connector=mock_minio, ocr_model=mock_model)
    actual = worker.set_extras(task=dummy_task)
    assert actual.extras is not None


def test_transform_content_error_no_content_type(mock_minio, mock_model: PaddleInferOCR, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="vvv/ssjpg",
    )
    worker = OCRWorker(file_connector=mock_minio, ocr_model=mock_model)
    dummy_task.extras = {}
    with open("tests/data/valid/identite.jpg", "rb") as f:
        expected_content = f.read()
        with pytest.raises(FileNotSupported):
            worker.transform_content(task=dummy_task, content=expected_content)


def test_transform_content_content_type_image(mock_minio, mock_model: PaddleInferOCR, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )

    worker = OCRWorker(file_connector=mock_minio, ocr_model=mock_model)
    with open("tests/data/valid/identite.jpg", "rb") as f:
        actual = worker.transform_content(task=dummy_task, content=f)
        assert isinstance(actual[0], Image.Image)


def test_transform_content_content_type_pdf(mock_minio, mock_model: PaddleInferOCR, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
        raw_filename="cerfa_13750-05-1.pdf",
        ext=".pdf",
        size=123456,
        content_type="application/pdf",  # Uncomment this line to simulate the absence of content_type
    )

    worker = OCRWorker(file_connector=mock_minio, ocr_model=mock_model)

    with open("tests/data/valid/cerfa_13750-05-1.pdf", "rb") as f:
        actual = worker.transform_content(task=dummy_task, content=f)
        assert isinstance(actual[0], Image.Image)
        assert len(actual) == 1


def test_predict_on_pages(mock_minio, mock_model: PaddleInferOCR, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    worker = OCRWorker(file_connector=mock_minio, ocr_model=mock_model)

    image = Image.open("tests/data/valid/identite.jpg")
    actual = worker.predict_on_pages(task=dummy_task, pages=[image])
    assert actual is not None


def test_predict_task_ocr_w_image(mock_minio, mock_model: PaddleInferOCR, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
        raw_filename="cerfa_13750-05-1.pdf",
        ext=".pdf",
        size=123456,
        content_type="application/pdf",  # Uncomment this line to simulate the absence of content_type
    )

    worker = OCRWorker(file_connector=mock_minio, ocr_model=mock_model)
    with open("tests/data/valid/cerfa_13750-05-1.pdf", "rb") as f:
        mock_minio.get_by_task_id.return_value = f
        task = worker.process_task_ocr(task=dummy_task)
        assert task.status == TaskStatus.COMPLETED.value
        mock_minio.delete_by_task_id.assert_called_once_with(user_id=dummy_task.user_id, task_id=dummy_task.id)
        assert task.output is not None
