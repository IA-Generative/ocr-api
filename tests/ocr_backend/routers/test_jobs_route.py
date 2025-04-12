import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from ocr_backend.main import app
from uuid import uuid4
from src.schemas.task import TaskModel
import shutil


@pytest.fixture()
def client():
    # Créer un client pour les tests
    client = TestClient(app)
    return client


@pytest.fixture()
def temp_file():
    # Créer un fichier temporaire pour l'upload
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"test content")
    temp_file.close()
    yield temp_file.name
    os.remove(temp_file.name)
    os.remove('./example.db')
    shutil.rmtree('tmp')


def test_upload_file(client, temp_file):
    user_id = str(uuid4())
    with open(temp_file, "rb") as file:
        response = client.post(
            f"/jobs/{user_id}",
            files={"file": (os.path.basename(temp_file), file,
                            "application/octet-stream")},
        )

    assert response.status_code == status.HTTP_201_CREATED
    assert TaskModel.model_validate(response.json()) is not None
