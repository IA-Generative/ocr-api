import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.schemas.templates import (
    TemplateModel,
)
from ocr_backend.routers.template import template_router


@pytest.fixture
def client():
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(template_router, prefix="/api")

    return TestClient(app)


@patch("src.models.templates.template_table.get_template_by_id")
def test_get_template_by_id(mock_get_template_by_id, client: TestClient):
    # Simulate a template returned by the mock
    mock_template = TemplateModel(
        id="1",
        user_id="user123",
        group_id="group1",
        description="Test Template",
        source_file="source_file.pdf",
        source_task_id="task123",
        page_number=1,
        vector=[1, 2, 3],
        extras={"source": "test"},
        created_at=1633036800,
        updated_at=1633036800,
    )
    mock_get_template_by_id.return_value = mock_template

    response = client.get("/api/template/1")
    assert response.status_code == 200
    assert response.json() == mock_template.model_dump()


@patch("src.models.templates.template_table.get_templates_by_user_id")
def test_get_templates_by_user_id(mock_get_templates_by_user_id, client: TestClient):
    # Simulate a template returned by the mock
    mock_template = TemplateModel(
        id="1",
        user_id="user123",
        group_id="group1",
        description="Test Template",
        source_file="source_file.pdf",
        source_task_id="task123",
        page_number=1,
        vector=[1, 2, 3],
        extras={"source": "test"},
        created_at=1633036800,
        updated_at=1633036800,
    )
    mock_get_templates_by_user_id.return_value = [mock_template]

    response = client.get("/api/templates/user/user123")
    assert response.status_code == 200
    assert response.json() == [mock_template.model_dump()]


@patch("src.models.templates.template_table.get_templates_by_group_id")
def test_get_templates_by_group_id(mock_get_templates_by_group_id, client: TestClient):
    # Simulate a template returned by the mock
    mock_template = TemplateModel(
        id="1",
        user_id="user123",
        group_id="group1",
        description="Test Template",
        source_file="source_file.pdf",
        source_task_id="task123",
        page_number=1,
        vector=[1, 2, 3],
        extras={"source": "test"},
        created_at=1633036800,
        updated_at=1633036800,
    )
    mock_get_templates_by_group_id.return_value = [mock_template]

    response = client.get("/api/templates/group/group1")
    assert response.status_code == 200
    assert response.json() == [mock_template.model_dump()]


@patch("src.models.templates.template_table.delete_template_by_id")
def test_delete_template_not_allowed(mock_delete_template_by_id, client: TestClient):
    mock_delete_template_by_id.return_value = None

    response = client.delete("/api/template/1")
    assert response.status_code == 403


@patch("src.models.templates.template_table.delete_template_by_id")
def test_delete_template(mock_delete_template_by_id, client: TestClient):
    mock_template = TemplateModel(
        id="1",
        user_id="user123",
        group_id="group1",
        description="Test Template",
        source_file="source_file.pdf",
        source_task_id="task123",
        page_number=1,
        vector=[1, 2, 3],
        extras={"source": "test"},
        created_at=1633036800,
        updated_at=1633036800,
    )
    mock_delete_template_by_id.return_value = mock_template

    response = client.delete(
        "/api/template/1",
        headers={"Authorization": "Bearer testtoken", "X-Roles": "admin"},
    )
    assert response.status_code == 200
    assert response.json() == mock_template.model_dump()


@patch("src.models.templates.template_table.delete_templates_by_user_id")
def test_delete_template_by_user(mock_delete_templates_by_user_id, client: TestClient):
    mock_template = TemplateModel(
        id="1",
        user_id="user123",
        group_id="group1",
        description="Test Template",
        source_file="source_file.pdf",
        source_task_id="task123",
        page_number=1,
        vector=[1, 2, 3],
        extras={"source": "test"},
        created_at=1633036800,
        updated_at=1633036800,
    )
    mock_delete_templates_by_user_id.return_value = [mock_template]

    response = client.delete(
        "/api/templates/user/user123",
        headers={
            "Authorization": "Bearer testtoken",
            "X-Roles": "user",
            "X-User-ID": "user12",
        },
    )
    assert response.status_code == 403

    response = client.delete(
        "/api/templates/user/test_user",
        headers={
            "Authorization": "Bearer testtoken",
            "X-Roles": "admin",
            "X-User-ID": "test_user",
        },
    )
    assert response.status_code == 200
    assert response.json() == [mock_template.model_dump()]


@patch("src.models.templates.template_table.delete_templates_by_group_id")
def test_delete_templates_by_group_id(mock_delete_templates_by_group_id, client: TestClient):
    mock_template = TemplateModel(
        id="1",
        user_id="user123",
        group_id="group1",
        description="Test Template",
        source_file="source_file.pdf",
        source_task_id="task123",
        page_number=1,
        vector=[1, 2, 3],
        extras={"source": "test"},
        created_at=1633036800,
        updated_at=1633036800,
    )
    mock_delete_templates_by_group_id.return_value = [mock_template]

    response = client.delete(
        "/api/templates/group/group1",
        headers={
            "Authorization": "Bearer testtoken",
            "X-Roles": "user",
            "X-User-ID": "user12",
        },
    )
    assert response.status_code == 403

    response = client.delete(
        "/api/templates/group/group1",
        headers={
            "Authorization": "Bearer testtoken",
            "X-Roles": "admin",
            "X-User-ID": "user123",
        },
    )
    assert response.status_code == 200
    assert response.json() == [mock_template.model_dump()]
