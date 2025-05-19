from fastapi.testclient import TestClient
from unittest.mock import patch
from ocr_backend.main import app
from src.schemas.task import TaskTable, TaskModel, TaskStatus


client = TestClient(app)


# Test pour récupérer une tâche par ID
@patch.object(TaskTable, "get_task_by_id")
def test_get_task_by_id(mock_get_task_by_id):
    # Simuler une tâche retournée
    mock_task = TaskModel(
        id="12345",
        user_id="user123",
        type="task_type_example",
        status=TaskStatus.QUEUED.value,
        percentage=50.0,
        created_at=1633036800,
        updated_at=1633036800,
        input=None,
        extras={"key": "value"},
    )

    mock_get_task_by_id.return_value = mock_task

    # Appel à l'API
    response = client.get("/tasks/12345")

    # Assertions
    assert response.status_code == 200
    assert response.json() == {
        "id": "12345",
        "user_id": "user123",
        "type": "task_type_example",
        "status": TaskStatus.QUEUED.value,
        "percentage": 50.0,
        "created_at": 1633036800,
        "updated_at": 1633036800,
        "input": None,
        "output": None,
        "extras": {"key": "value"},
    }


@patch.object(TaskTable, "get_task_by_id")
def test_get_task_by_id_not_found(mock_get_task_by_id):
    # Simuler que la tâche n'est pas trouvée
    mock_get_task_by_id.return_value = None

    # Appel à l'API
    response = client.get("/tasks/12345")

    # Assertions
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@patch.object(TaskTable, "get_tasks_by_user_id")
def test_get_task_by_user_not_found(mock_get_task_by_user):
    # Simuler que la tâche n'est pas trouvée
    mock_get_task_by_user.return_value = []

    # Appel à l'API
    response = client.get("/tasks/user/titi")

    # Assertions
    assert response.status_code == 404
    assert response.json() == {"detail": "No tasks found for this user"}


@patch.object(TaskTable, "get_tasks_by_user_id")
def test_get_task_by_user(mock_get_task_by_user):
    # Simuler que la tâche n'est pas trouvée
    mock_task_1 = TaskModel(
        id="12345",
        user_id="mic",
        type="task_type_example",
        status=TaskStatus.QUEUED.value,
        percentage=50.0,
        created_at=1633036800,
        updated_at=1633036800,
        input=None,
        extras={"key": "value"},
    )

    mock_task_2 = TaskModel(
        id="12345",
        user_id="mic",
        type="task_type_example",
        status=TaskStatus.QUEUED.value,
        percentage=1,
        input=None,
        created_at=1633036800,
        updated_at=1633036800,
        extras={"key": "value"},
    )

    mock_get_task_by_user.return_value = [mock_task_1, mock_task_2]
    # Appel à l'API
    response = client.get("/tasks/user/mic2")

    # Assertions
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "12345",
            "user_id": "mic",
            "type": "task_type_example",
            "status": TaskStatus.QUEUED.value,
            "percentage": 50.0,
            "created_at": 1633036800,
            "updated_at": 1633036800,
            "extras": {"key": "value"},
            "input": None,
            "output": None,
        },
        {
            "id": "12345",
            "user_id": "mic",
            "type": "task_type_example",
            "status": TaskStatus.QUEUED.value,
            "percentage": 1,
            "created_at": 1633036800,
            "updated_at": 1633036800,
            "extras": {"key": "value"},
            "input": None,
            "output": None,
        },
    ]
