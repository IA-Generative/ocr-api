import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

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
    response = client.get("/api/tasks/12345")

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
        "position": None,
        "extras": {"key": "value"},
        "content_hash": None,
    }


@patch.object(TaskTable, "get_task_by_id")
def test_get_task_by_id_not_found(mock_get_task_by_id):
    # Simuler que la tâche n'est pas trouvée
    mock_get_task_by_id.return_value = None

    # Appel à l'API
    response = client.get("/api/tasks/12345")

    # Assertions
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


@patch.object(TaskTable, "get_tasks_by_user_id")
def test_get_task_by_user_not_found(mock_get_task_by_user):
    # Simuler que la tâche n'est pas trouvée
    mock_get_task_by_user.return_value = []

    # Appel à l'API
    response = client.get("/api/tasks/user/titi")

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
    response = client.get("/api/tasks/user/mic2")

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
            "position": None,
            "output": None,
            "content_hash": None,
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
            "position": None,
            "output": None,
            "content_hash": None,
        },
    ]


@patch("ocr_backend.routers.task.s3_client_connector")
@patch.object(TaskTable, "delete_tasks_by_date_and_status")
def test_delete_tasks_by_date_and_status_success(
    mock_delete,
    mock_s3,
):
    # Données de test
    mock_tasks = [
        TaskModel(
            id="task1",
            user_id="user456",
            type="test",
            status=TaskStatus.COMPLETED.value,
            percentage=0.0,
            created_at=int(datetime.now().timestamp()),
            updated_at=int(datetime.now().timestamp()),
            input=None,
            extras={"initial": True},
        ),
        TaskModel(
            id="task2",
            user_id="user456",
            type="test",
            status=TaskStatus.COMPLETED.value,
            percentage=0.0,
            created_at=int(datetime.now().timestamp()),
            updated_at=int(datetime.now().timestamp()),
            input=None,
            extras={"initial": True},
        ),
    ]
    mock_delete.return_value = mock_tasks

    start = datetime.now() - timedelta(minutes=10)
    end = datetime.now()

    # Patch des dépendances
    response = client.delete(
        "/api/v1/tasks/",
        params={
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "status": TaskStatus.COMPLETED.value,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    for task in mock_tasks:
        mock_s3.delete_by_task_id.assert_any_call(user_id=task.user_id, task_id=task.id)


@pytest.mark.asyncio
async def test_delete_tasks_by_date_and_status_not_found():
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 3)

    with patch("ocr_backend.routers.task.task_table") as mock_task_table:
        mock_task_table.delete_tasks_by_date_and_status.return_value = []

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.delete(
                "/api/v1/tasks/",
                params={
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                    "status": TaskStatus.COMPLETED.value,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
