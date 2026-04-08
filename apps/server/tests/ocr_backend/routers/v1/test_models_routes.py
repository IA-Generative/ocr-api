import pytest


from fastapi.testclient import TestClient
from fastapi import FastAPI


@pytest.fixture
def client() -> TestClient:
    from ocr_backend.routers.v1.models import router as models_router

    app = FastAPI()
    app.include_router(models_router)

    return TestClient(app)


def test_list_models(client: TestClient) -> None:
    response = client.get("/models", headers={"Authorization": "Bearer secret-api"})

    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "list"
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0
    model = data["data"][0]
    assert "id" in model
    assert "object" in model
    assert "created" in model
    assert "owned_by" in model
