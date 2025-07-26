from fastapi.testclient import TestClient
from ocr_backend.main import app


client = TestClient(app)


def test_get_health():
    # Appel à la route /health
    response = client.get("/api/health")

    # Assertions
    assert response.status_code == 200
    data = response.json()

    # Vérifier la structure et le contenu de la réponse
    assert "name" in data
    assert "version" in data
    assert "up_time" in data
    assert "status" in data
    assert data["status"] == "healthy"

    assert "dependencies" in data
    assert isinstance(data["dependencies"], list)
    assert len(data["dependencies"]) > 0
    assert "version" in data["dependencies"][0]
    assert "up_time" in data["dependencies"][0]
    assert data["dependencies"][0]["status"] == "healthy"
