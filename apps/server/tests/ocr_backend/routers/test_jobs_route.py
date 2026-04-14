import glob
import json
from pathlib import Path
import os
import tempfile
from uuid import uuid4
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from ocr_backend.connectors import s3_client_connector
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from src.connector.db_connector import Base

from src.schemas.task import TaskModel, TaskStatus, TaskOperation
from src.schemas.input import RegionOfInterest


@pytest.fixture()
def client(async_engine):
    """Client avec SQLite - tables créées pour les tests"""
    from ocr_backend.routers.jobs import router as jobs_router, get_db_session
    import asyncio

    # Créer les tables une fois
    async def setup():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(setup())

    app = FastAPI()
    app.include_router(jobs_router, prefix="/api")

    # Override: get_db_session doit retourner une AsyncSession vraie
    AsyncTestingSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncTestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db

    client = TestClient(app)
    yield client

    # Cleanup
    async def cleanup():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(cleanup())


@pytest.fixture()
def create_table(async_engine):
    """Fixture pour créer les tables avant les tests et les supprimer après"""
    import asyncio

    # Créer les tables de manière synchrone
    async def create_and_drop():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    # Utiliser asyncio.run pour exécuter dans un event loop
    gen = create_and_drop()
    try:
        asyncio.run(gen.__anext__())
    except StopAsyncIteration:
        pass

    yield

    try:
        asyncio.run(gen.__anext__())
    except StopAsyncIteration:
        pass


@pytest.fixture()
def temp_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"test content")
    temp_file.close()
    yield temp_file.name
    os.remove(temp_file.name)


def test_upload_file(client):
    user_id = str(uuid4())

    for img_path in glob.glob("tests/data/valid/*"):
        if not Path(img_path).is_dir:
            with open(img_path, "rb") as image_file:
                files = {"file": (img_path, image_file, "multipart/form-data")}

                # Effectuer l'appel à l'API pour uploader le fichier
                response = client.post(
                    f"/api/jobs/{user_id}",
                    files=files,
                )

            # Vérifier la réponse
            assert response.status_code == 201
            response_model = TaskModel(**response.json())
            assert response_model.status == TaskStatus.QUEUED.value
            assert response_model.user_id == user_id

            # Vérifier que le fichier est bien enregistré dans Minio
            task_id = response_model.id
            file_from_minio = s3_client_connector.get_by_task_id(user_id, task_id)

            assert os.path.exists(file_from_minio)


def test_upload_files_success(client):
    """Test the api/jobs/ route with authentication"""
    user_id = "test_user"

    # Mock authentication - you'll need to adapt this based on your actual auth implementation

    path = "tests/data/valid/cerfa_11573-09-filled.pdf"

    with open(path, "rb") as image_file:
        files = {"file": (path, image_file, "application/pdf")}
        data = {
            "group_id": "TEST_GROUP",
            "task_operation": TaskOperation.DEFAULT.value,
        }

        # Call the API endpoint
        response = client.post(
            "/api/jobs/",
            files=files,
            data=data,
        )
    # Verify response
    assert response.status_code == 201
    response_model = TaskModel(**response.json())
    assert response_model.status == TaskStatus.QUEUED.value
    assert response_model.user_id == user_id
    assert response_model.group_id == "TEST_GROUP"
    assert response_model.type == TaskOperation.DEFAULT.value

    # Verify file is saved in Minio
    task_id = response_model.id
    file_from_minio = s3_client_connector.get_by_task_id(user_id, task_id)
    assert os.path.exists(file_from_minio)


def test_upload_files_failed_invalid_task_type(client):
    """Test the api/jobs/ route with authentication"""

    # Mock authentication - you'll need to adapt this based on your actual auth implementation

    path = "tests/data/valid/cerfa_11573-09-filled.pdf"

    with open(path, "rb") as image_file:
        files = {"file": (path, image_file, "application/pdf")}
        data = {
            "group_id": "TEST_GROUP",
            "task_operation": "task_operation_invalid",  # Invalid operation to trigger failure
        }

        # Call the API endpoint
        response = client.post(
            "/api/jobs/",
            files=files,
            data=data,
        )
    # Verify response
    assert response.status_code == 422


def test_upload_image_file_failed_input_string(client):
    """Test the api/jobs/ route with authentication"""

    # Mock authentication - you'll need to adapt this based on your actual auth implementation

    path = "tests/data/valid/formulaire-cerfa-complete.png"

    with open(path, "rb") as image_file:
        files = {"file": (path, image_file, "image/png")}
        data = {
            "group_id": "TEST_GROUP",
            "task_operation": TaskOperation.SAVE_TEMPLATE.value,  # Invalid operation to trigger failure
        }

        # Call the API endpoint
        response = client.post(
            "/api/jobs/",
            files=files,
            data=data,
        )
    # Verify response
    assert response.status_code == 201


def test_upload_files_valid_pdf_input_string(client):
    """Test the api/jobs/ route with authentication"""
    user_id = "test_user"

    # Mock authentication - you'll need to adapt this based on your actual auth implementation

    path = "tests/data/valid/cerfa_11573-09-filled.pdf"

    with open(path, "rb") as image_file:
        files = {"file": (path, image_file, "application/pdf")}
        data = {
            "group_id": "TEST_GROUP",
            "task_operation": TaskOperation.SAVE_TEMPLATE.value,  # Invalid operation to trigger failure
            "input_json_string": json.dumps(
                [RegionOfInterest(interest_zone=[], labels="").model_dump()]
            ),  # Invalid JSON to trigger failure
        }

        # Call the API endpoint
        response = client.post(
            "/api/jobs/",
            files=files,
            data=data,
        )
    # Verify response
    assert response.status_code == 201
    response_model = TaskModel(**response.json())
    assert response_model.status == TaskStatus.QUEUED.value
    assert response_model.user_id == user_id
    assert response_model.group_id == "TEST_GROUP"
    assert response_model.type == TaskOperation.SAVE_TEMPLATE.value


def test_upload_files_valid_image_input_string(client):
    """Test the api/jobs/ route with authentication"""

    # Mock authentication - you'll need to adapt this based on your actual auth implementation

    path = "tests/data/valid/formulaire-cerfa-complete.png"

    with open(path, "rb") as image_file:
        files = {"file": (path, image_file, "image/png")}
        data = {
            "group_id": "TEST_GROUP",
            "task_operation": TaskOperation.SAVE_TEMPLATE.value,  # Invalid operation to trigger failure
            "interest_zone": json.dumps(
                [RegionOfInterest(interest_zone=[], labels="").model_dump()]
            ),  # Invalid JSON to trigger failure
        }

        # Call the API endpoint
        response = client.post(
            "/api/jobs/",
            files=files,
            data=data,
        )
    # Verify response
    assert response.status_code == 201
    response_model = TaskModel(**response.json())
    assert response_model.status == TaskStatus.QUEUED.value
    assert response_model.user_id == "test_user"
    assert response_model.group_id == "TEST_GROUP"
    assert response_model.type == TaskOperation.SAVE_TEMPLATE.value


def test_upload_files_valid_pdf_raised_error(client):
    """Test the api/jobs/ route with authentication"""
    # Mock authentication - you'll need to adapt this based on your actual auth implementation

    path = "tests/data/valid/cerfa_11573-09-filled.pdf"
    with patch("src.connector.broker_connector.celery_app.send_task") as mock_send_task:
        mock_send_task.side_effect = Exception("Mocked error for testing")

        with open(path, "rb") as image_file:
            files = {"file": (path, image_file, "application/pdf")}
            data = {
                "group_id": "TEST_GROUP",
                "task_operation": TaskOperation.SAVE_TEMPLATE.value,
                "input_json_string": json.dumps([RegionOfInterest(interest_zone=[], labels="").model_dump()]),
            }

            # Call the API endpoint
            response = client.post(
                "/api/jobs/",
                files=files,
                data=data,
            )
            assert response.status_code == 500, response.json()


def test_upload_files_v1_unauthorized(client):
    """Test the v1/jobs/ route without authentication"""
    from ocr_backend.core.security.factory import TokenVerifier

    with patch.object(TokenVerifier, "verify") as mock_verify:
        mock_verify.return_value = False
        with tempfile.NamedTemporaryFile(suffix=".pdf") as temp_file:
            temp_file.write(b"test content")
            temp_file.seek(0)

            files = {"file": ("test.pdf", temp_file, "application/pdf")}

            # Call without authentication headers
            response = client.post(
                "/api/jobs/",
                files=files,
                headers={},
                data={
                    "group_id": "TEST_GROUP",
                    "task_operation": TaskOperation.SAVE_TEMPLATE.value,  # Invalid operation to trigger failure
                    "input_json_string": json.dumps(
                        [RegionOfInterest(interest_zone=[], labels="").model_dump()]
                    ),  # Invalid JSON to trigger failure
                },
            )

            # Should return 401 Unauthorized or 403 Forbidden
            assert response.status_code in [401, 403]


def test_upload_files_v1_with_input_json(client):
    """Test the v1/jobs/ route with input_json_string parameter"""
    user_id = "test_user"

    headers = {
        "Authorization": f"Bearer mock_token_{user_id}",
        "X-User-ID": user_id,
    }

    with open("tests/data/valid/cerfa_13750-05-1.pdf", "rb") as temp_file:
        files = {"file": ("test.pdf", temp_file, "application/pdf")}
        data = {
            "group_id": "TEST_GROUP",
            "task_operation": TaskOperation.SAVE_TEMPLATE.value,  # Invalid operation to trigger failure
            "input_json_string": json.dumps([RegionOfInterest(interest_zone=[], labels="").model_dump()]),
        }

        response = client.post(
            "/api/jobs/",
            files=files,
            data=data,
            headers=headers,
        )

        assert response.status_code == 201, response.json()
        response_model = TaskModel(**response.json())
        assert response_model.status == TaskStatus.QUEUED.value
        assert response_model.user_id == user_id
