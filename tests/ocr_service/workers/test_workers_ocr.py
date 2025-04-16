import pytest
from unittest.mock import MagicMock
from ocr_service.workers.ocr_worker import OCRWorker, EmptyContentException
from src.schemas.task import TaskModel
from ocr_service.models.base import BaseModelPrediction
from ocr_service.models.surya_ocr import SuryaOCR
from ocr_service.configs.surya import SuryaSetting

settings = SuryaSetting()


@pytest.fixture
def dummy_task():
    return TaskModel(
        id="task_id_123",
        user_id="user_456",
        extras={}
    )


@pytest.fixture
def mock_minio():
    return MagicMock()


@pytest.fixture
def mock_model() -> SuryaOCR:
    return SuryaOCR(checkpoint_detection=settings.SURYA_DETECTION_FOLDER, checkpoint_recognition=settings.SURYA_RECOGNITION_FOLDER)


def test_get_content_file_success(mock_minio, mock_model, dummy_task):
    expected_content = b"fake-bytes-content"
    mock_minio.get_by_task_id.return_value = expected_content

    worker = OCRWorker(minio_connector=mock_minio, ocr_model=mock_model)
    content = worker.get_content_file(task=dummy_task)

    assert content == expected_content
    mock_minio.get_by_task_id.assert_called_once_with(
        user_id="user_456", task_id="task_id_123")


def test_get_content_file_none(mock_minio, mock_model, dummy_task):
    mock_minio.get_by_task_id.return_value = None

    worker = OCRWorker(minio_connector=mock_minio, ocr_model=mock_model)

    with pytest.raises(EmptyContentException):
        worker.get_content_file(task=dummy_task)

    mock_minio.get_by_task_id.assert_called_once()


def test_get_content_file_exception(mock_minio, mock_model, dummy_task):
    mock_minio.get_by_task_id.side_effect = Exception("Connection error")

    worker = OCRWorker(minio_connector=mock_minio, ocr_model=mock_model)

    with pytest.raises(Exception) as exc_info:
        worker.get_content_file(task=dummy_task)

    assert "Connection error" in str(exc_info.value)
    mock_minio.get_by_task_id.assert_called_once()
