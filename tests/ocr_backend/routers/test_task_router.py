from fastapi.testclient import TestClient
from unittest.mock import patch
from ocr_backend.main import app
from src.schemas.task import TaskTable, TaskModel


client = TestClient(app)


# Test pour récupérer une tâche par ID
@patch.object(TaskTable, "get_task_by_id")
def test_get_task_by_id(mock_get_task_by_id):
    # Simuler une tâche retournée
    mock_task = TaskModel(
        id="12345",
        user_id="user123",
        type="task_type_example",
        status="queued",
        percentage=50.0,
        created_at=1633036800,
        updated_at=1633036800,
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
        "status": "queued",
        "percentage": 50.0,
        "created_at": 1633036800,
        "updated_at": 1633036800,
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
