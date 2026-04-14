from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from ocr_backend.routers.task import (
    router as task_router,
    get_task_service,
    get_db_session,
)
from src.schemas.task import TaskModel, TaskStatus
from src.services.task_service import TaskService
from ocr_backend.core.security.token import RequestContext
from fastapi import FastAPI

app = FastAPI()
app.include_router(task_router)
client = TestClient(app)


def create_mock_context(is_admin: bool = False, user_id: str = "test-user-id") -> RequestContext:
    """Helper pour créer un contexte mocké"""
    ctx = MagicMock(spec=RequestContext)
    ctx.is_admin = is_admin
    ctx.user_id = user_id
    return ctx


@patch("ocr_backend.routers.task.get_task_service")
@patch("ocr_backend.routers.task.TokenVerifier")
def test_get_task_by_id(mock_token_verifier, mock_get_service):
    # Simuler une tâche retournée
    mock_task = TaskModel(
        id="12345",
        user_id="test_user",
        type="task_type_example",
        status=TaskStatus.QUEUED.value,
        percentage=50.0,
        created_at=1633036800,
        updated_at=1633036800,
        input=None,
        extras={"key": "value"},
    )

    # Configure les mocks
    mock_service = MagicMock(spec=TaskService)
    mock_service.get_tasks_by_id = AsyncMock(return_value=[mock_task])
    mock_service.get_position_in_queue = AsyncMock(return_value=1)
    mock_get_service.return_value = mock_service

    mock_ctx = create_mock_context(user_id="test_user")
    mock_token_verifier.return_value = mock_ctx

    app.dependency_overrides[get_task_service] = lambda: mock_service
    app.dependency_overrides[get_db_session] = lambda: MagicMock()

    try:
        # Appel à l'API
        response = client.get("/tasks/12345")

        # Assertions
        assert response.status_code == 200
        assert response.json() == {
            "id": "12345",
            "user_id": "test_user",
            "type": "task_type_example",
            "status": TaskStatus.QUEUED.value,
            "percentage": 50.0,
            "created_at": 1633036800,
            "updated_at": 1633036800,
            "input": None,
            "output": None,
            "position": 1,
            "extras": {"key": "value"},
            "content_hash": None,
            "group_id": None,
            "parameters": None,
        }
    finally:
        app.dependency_overrides.clear()


@patch("ocr_backend.routers.task.get_task_service")
@patch("ocr_backend.routers.task.TokenVerifier")
def test_get_task_by_id_not_found(mock_token_verifier, mock_get_service):
    # Configure les mocks
    mock_service = MagicMock(spec=TaskService)
    mock_service.get_tasks_by_id = AsyncMock(return_value=[])
    mock_get_service.return_value = mock_service

    mock_ctx = create_mock_context(user_id="test_user")
    mock_token_verifier.return_value = mock_ctx

    app.dependency_overrides[get_task_service] = lambda: mock_service
    app.dependency_overrides[get_db_session] = lambda: MagicMock()

    try:
        # Appel à l'API
        response = client.get("/tasks/12345")

        # Assertions
        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}
    finally:
        app.dependency_overrides.clear()


@patch("ocr_backend.routers.task.get_task_service")
@patch("ocr_backend.routers.task.TokenVerifier")
def test_get_task_by_user_not_found(mock_token_verifier, mock_get_service):
    # Configure les mocks
    mock_service = MagicMock(spec=TaskService)
    mock_service.get_tasks_by_user_id = AsyncMock(return_value=[])
    mock_service.count_tasks_by_user_id = AsyncMock(return_value=0)
    mock_get_service.return_value = mock_service

    mock_ctx = create_mock_context(user_id="test_user")
    mock_token_verifier.return_value = mock_ctx

    app.dependency_overrides[get_task_service] = lambda: mock_service
    app.dependency_overrides[get_db_session] = lambda: MagicMock()

    try:
        # Appel à l'API
        response = client.get("/tasks/user/")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
    finally:
        app.dependency_overrides.clear()


@patch("ocr_backend.routers.task.get_task_service")
@patch("ocr_backend.routers.task.TokenVerifier")
def test_get_task_by_user(mock_token_verifier, mock_get_service):
    # Créer les tâches de test
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
        id="12346",
        user_id="mic",
        type="task_type_example",
        status=TaskStatus.QUEUED.value,
        percentage=1,
        input=None,
        created_at=1633036800,
        updated_at=1633036800,
        extras={"key": "value"},
    )

    # Configure les mocks
    mock_service = MagicMock(spec=TaskService)
    mock_service.get_tasks_by_user_id = AsyncMock(return_value=[mock_task_1, mock_task_2])
    mock_service.count_tasks_by_user_id = AsyncMock(return_value=2)
    mock_get_service.return_value = mock_service

    mock_ctx = create_mock_context(user_id="mic")
    mock_token_verifier.return_value = mock_ctx

    app.dependency_overrides[get_task_service] = lambda: mock_service
    app.dependency_overrides[get_db_session] = lambda: MagicMock()

    try:
        # Appel à l'API
        response = client.get("/tasks/user/")

        # Assertions
        assert response.status_code == 200
        assert response.json()
    finally:
        app.dependency_overrides.clear()


@patch("ocr_backend.routers.task.s3_client_connector")
@patch("ocr_backend.routers.task.TokenVerifier")
def test_delete_tasks_by_date_and_status_success(
    mock_token_verifier,
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

    # Configure les mocks
    mock_service = MagicMock(spec=TaskService)
    mock_service.delete_tasks_by_date_and_status = AsyncMock(return_value=mock_tasks)
    mock_db = MagicMock()

    # Mock le contexte admin
    mock_ctx = create_mock_context(is_admin=True)
    mock_token_verifier.return_value = mock_ctx

    # Override les dépendances FastAPI
    app.dependency_overrides[get_task_service] = lambda: mock_service
    app.dependency_overrides[get_db_session] = lambda: mock_db

    start = datetime.now() - timedelta(minutes=10)
    end = datetime.now()

    try:
        # Test avec rôle admin - succès
        response = client.delete(
            "/v1/tasks/",
            params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "status": TaskStatus.COMPLETED.value,
            },
            headers={
                "x-user-id": "test-user-id",
                "x-user-email": "test@example.com",
                "x-roles": "admin,user",
                "authorization": "Bearer test-token-abc",
            },
        )

        assert response.status_code == 204
        for task in mock_tasks:
            mock_s3.delete_by_task_id.assert_any_call(user_id=task.user_id, task_id=task.id)

        # Test avec rôle user (pas admin) - 403
        mock_ctx.is_admin = False
        response = client.delete(
            "/v1/tasks/",
            params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "status": TaskStatus.COMPLETED.value,
            },
            headers={
                "x-user-id": "test-user-id",
                "x-user-email": "test@example.com",
                "x-roles": "user",
            },
        )

        assert response.status_code == 403
    finally:
        app.dependency_overrides.clear()


@patch("ocr_backend.routers.task.TokenVerifier")
def test_delete_tasks_by_date_and_status_not_found(mock_token_verifier):
    # Configure les mocks
    mock_service = MagicMock(spec=TaskService)
    mock_service.delete_tasks_by_date_and_status = AsyncMock(return_value=[])
    mock_db = MagicMock()

    # Mock le contexte admin
    mock_ctx = create_mock_context(is_admin=True)
    mock_token_verifier.return_value = mock_ctx

    # Override les dépendances FastAPI
    app.dependency_overrides[get_task_service] = lambda: mock_service
    app.dependency_overrides[get_db_session] = lambda: mock_db

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 3)

    try:
        response = client.delete(
            "/v1/tasks/",
            params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "status": TaskStatus.COMPLETED.value,
            },
            headers={
                "x-user-id": "test-user-id",
                "x-user-email": "test@example.com",
                "x-roles": "admin,user",
                "authorization": "Bearer test-token-abc",
            },
        )

        assert response.status_code == 204
    finally:
        app.dependency_overrides.clear()
