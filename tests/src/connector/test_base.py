# test_file_connector.py

import pytest
from unittest.mock import create_autospec
from src.connector.base import BaseFileConnector
from src.schemas.health import Health


@pytest.fixture
def mock_file_connector():
    mock = create_autospec(BaseFileConnector, instance=True)
    mock.get_health.return_value = Health(
        status="healthy",
        version="1.0",
        up_time="2023-10-01T00:00:00Z",
        dependencies=[],
        name="mock",
    )
    mock.get_by_task_id.return_value = "mocked_file_path"
    mock.save.return_value = "saved_file_path"
    mock.delete_by_task_id.return_value = True
    mock.delete_by_user_id.return_value = True

    return mock


def test_get_health(mock_file_connector):
    health = mock_file_connector.get_health()
    assert health == Health(
        status="healthy",
        version="1.0",
        up_time="2023-10-01T00:00:00Z",
        dependencies=[],
        name="mock",
    )
    mock_file_connector.get_health.assert_called_once()


def test_get_by_task_id(mock_file_connector):
    result = mock_file_connector.get_by_task_id("user123", "task456")
    assert result == "mocked_file_path"
    mock_file_connector.get_by_task_id.assert_called_once_with("user123", "task456")


def test_save_file(mock_file_connector):
    result = mock_file_connector.save("user123", "task456", "/some/path")
    assert result == "saved_file_path"
    mock_file_connector.save.assert_called_once_with("user123", "task456", "/some/path")


def test_delete_by_task_id(mock_file_connector):
    result = mock_file_connector.delete_by_task_id("user123", "task456")
    assert result is True
    mock_file_connector.delete_by_task_id.assert_called_once_with("user123", "task456")


def test_delete_by_user_id(mock_file_connector):
    result = mock_file_connector.delete_by_user_id("user123")
    assert result is True
    mock_file_connector.delete_by_user_id.assert_called_once_with("user123")
