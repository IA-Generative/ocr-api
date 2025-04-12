import os
import shutil
import pytest
from unittest.mock import patch
from src.connector.fs import FileSystemConnector


@pytest.fixture
def file_system_connector():
    return FileSystemConnector(base_folder="./tmp_test")


def test_get_by_task_id_found(file_system_connector):

    user_id = "user1"
    task_id = "task1"
    folder_task = os.path.join(
        file_system_connector._FileSystemConnector__folder, user_id, task_id)

    os.makedirs(folder_task, exist_ok=True)

    result = file_system_connector.get_by_task_id(user_id, task_id)

    assert result == folder_task  # Vérifie que le bon dossier a été retourné
    shutil.rmtree(folder_task)  # Nettoyage après le test


def test_get_by_task_id_not_found(file_system_connector):

    user_id = "user1"
    task_id = "task_not_found"

    with pytest.raises(FileNotFoundError):
        file_system_connector.get_by_task_id(user_id, task_id)


@patch("shutil.copy2")
def test_save(mock_copy2, file_system_connector):

    user_id = "user1"
    task_id = "task1"
    file_path = "path/to/file.txt"
    folder_task = os.path.join(
        file_system_connector._FileSystemConnector__folder, user_id, task_id)

    result = file_system_connector.save(user_id, task_id, file_path)

    mock_copy2.assert_called_once_with(file_path, os.path.join(
        folder_task, os.path.basename(file_path)))
    assert result == "./tmp_test/user1/task1/file.txt"


@patch("shutil.rmtree")
def test_delete_by_task_id(mock_rmtree, file_system_connector):
    # Teste la suppression par task_id
    user_id = "user1"
    task_id = "task1"
    folder_task = os.path.join(
        file_system_connector._FileSystemConnector__folder, user_id, task_id)

    os.makedirs(folder_task, exist_ok=True)

    result = file_system_connector.delete_by_task_id(user_id, task_id)

    mock_rmtree.assert_called_once_with(folder_task)
    assert result is True

    result = file_system_connector.delete_by_task_id(
        user_id, "non_existent_task")
    assert result is False


@patch("shutil.rmtree")
def test_delete_by_user_id(mock_rmtree, file_system_connector):

    user_id = "user1"
    folder_user = os.path.join(
        file_system_connector._FileSystemConnector__folder, user_id)

    os.makedirs(folder_user, exist_ok=True)
    result = file_system_connector.delete_by_user_id(user_id)
    mock_rmtree.assert_called_once_with(folder_user)
    assert result is True

    result = file_system_connector.delete_by_user_id("non_existent_user")
    assert result is False


@pytest.fixture(scope="session", autouse=True)
def cleanup_tmp_test():
    """ Teardown to remove tmp_test folder after tests """
    yield

    tmp_folder = "./tmp_test"
    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)
