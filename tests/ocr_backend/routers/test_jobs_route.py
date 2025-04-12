import json
import tempfile
import os
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from ocr_backend.main import app
from ocr_backend.clients import minio_connector, redis_client, redis_settings, minio_settings
from src.internal.db import engine
from src.schemas.task import task_table, TaskModel


@pytest.fixture()
def client():
    client = TestClient(app)
    return client


@pytest.fixture()
def temp_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"test content")
    temp_file.close()
    yield temp_file.name
    os.remove(temp_file.name)


def test_upload_file(client, temp_file):
    user_id = str(uuid4())

    # Préparer le fichier à uploader
    with open(temp_file, "rb") as file:
        # Effectuer l'appel à l'API pour uploader le fichier
        response = client.post(
            f"/jobs/{user_id}",
            files={"file": (os.path.basename(temp_file), file,
                            "application/octet-stream")},
        )

    # Vérifier la réponse
    assert response.status_code == 201
    response_model = TaskModel(**response.json())
    assert response_model.status == "pending"
    assert response_model.user_id == user_id

    # Vérifier que le fichier est bien enregistré dans Minio
    task_id = response_model.id
    file_from_minio = minio_connector.get_by_task_id(user_id, task_id)
    assert file_from_minio.read() == b"test content"

    # Vérifier que la tâche est bien ajoutée dans Redis
    task_in_redis = redis_client.lpop(redis_settings.REDIS_QUEUE_NAME)
    assert task_in_redis is not None
    task_in_redis_data = json.loads(task_in_redis)
    assert task_in_redis_data["user_id"] == user_id
    assert task_in_redis_data["status"] == "pending"
    assert task_table.get_task_by_id(task_id=task_id) is not None
