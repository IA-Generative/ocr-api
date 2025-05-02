import glob
import os
import tempfile
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from ocr_backend.connectors import s3_client_connector
from ocr_backend.main import app
from src.schemas.task import TaskModel, TaskStatus


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

    for img_path in glob.glob("tests/data/valid/*"):
        with open(img_path, "rb") as image_file:
            files = {"file": (img_path, image_file, "multipart/form-data")}

            # Effectuer l'appel à l'API pour uploader le fichier
            response = client.post(
                f"/jobs/{user_id}",
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
        assert isinstance(file_from_minio.read(), bytes)
