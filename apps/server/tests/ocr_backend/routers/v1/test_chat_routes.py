import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Block real connectors + stub missing sibling modules before any import
# ---------------------------------------------------------------------------
_mock_connectors = MagicMock()
sys.modules.setdefault("ocr_backend.connectors", _mock_connectors)
# files router was removed; stub it so __init__ doesn't fail
sys.modules.setdefault("ocr_backend.routers.v1.files", MagicMock(router=MagicMock()))

# ---------------------------------------------------------------------------
# Shared mock task returned by sending_file_to_ocr_service
# ---------------------------------------------------------------------------
MOCK_TASK = {
    "id": "task-123",
    "status": "queued",
    "type": "ocr",
    "user_id": "user-1",
    "group_id": None,
    "percentage": 0.0,
    "input": None,
    "output": None,
    "created_at": 1712345678,
    "updated_at": 1712345678,
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> TestClient:
    from ocr_backend.routers.v1.chat import router as chat_router

    app = FastAPI()
    app.include_router(chat_router)
    return TestClient(app)


@pytest.fixture
def valid_request() -> dict:
    return {
        "model": "ocr-v1",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract text from this image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": "https://example.com/doc.png"},
                    },
                ],
            }
        ],
        "stream": False,
    }


@pytest.fixture(autouse=True)
def mock_utils(tmp_path: Path):
    """Mock file retrieval and OCR service for all tests."""
    fake_file = tmp_path / "doc.png"
    fake_file.write_bytes(b"\x89PNG")

    with (
        patch(
            "ocr_backend.routers.v1.chat.retrieve_file_or_image_from_chat_message",
            return_value=fake_file,
        ),
        patch(
            "ocr_backend.routers.v1.chat.sending_file_to_ocr_service",
            return_value=MOCK_TASK,
        ),
    ):
        yield


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_chat_completion_invalid_model(client: TestClient, valid_request: dict) -> None:
    request_data = {**valid_request, "model": "unsupported-model"}
    response = client.post(
        "/chat/completions",
        json=request_data,
        headers={"Authorization": "Bearer secret-api"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported model unsupported-model"


def test_chat_completion_returns_openai_format(client: TestClient, valid_request: dict) -> None:
    response = client.post(
        "/chat/completions",
        json=valid_request,
        headers={"Authorization": "Bearer secret-api"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["object"] == "chat.completion"
    assert data["model"] == "ocr-v1"
    assert data["id"] == MOCK_TASK["id"]
    assert len(data["choices"]) == 1
    assert data["choices"][0]["message"]["role"] == "assistant"
    assert isinstance(data["choices"][0]["message"]["content"], str)
    assert data["choices"][0]["finish_reason"] == "stop"
    assert "usage" in data


def test_chat_completion_content_contains_task_json(client: TestClient, valid_request: dict) -> None:
    response = client.post(
        "/chat/completions",
        json=valid_request,
        headers={"Authorization": "Bearer secret-api"},
    )
    assert response.status_code == 200
    content = response.json()["choices"][0]["message"]["content"]
    task_data = json.loads(content)
    assert task_data["id"] == MOCK_TASK["id"]
    assert task_data["status"] == MOCK_TASK["status"]


def test_chat_completion_requires_auth(client: TestClient, valid_request: dict) -> None:
    response = client.post("/chat/completions", json=valid_request)
    assert response.status_code == 401


def test_chat_completion_missing_messages(client: TestClient) -> None:
    response = client.post(
        "/chat/completions",
        json={"model": "ocr-v1"},
        headers={"Authorization": "Bearer secret-api"},
    )
    assert response.status_code == 422


def test_chat_completion_no_image_raises_error(client: TestClient) -> None:
    """Content list with no image or file part → 422."""
    request_data = {
        "model": "ocr-v1",
        "messages": [{"role": "user", "content": [{"type": "text", "text": "No image here."}]}],
        "stream": False,
    }
    response = client.post(
        "/chat/completions",
        json=request_data,
        headers={"Authorization": "Bearer secret-api"},
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("image_url" in err["msg"] for err in errors)


def test_chat_completion_tempfile_deleted_after_request(
    client: TestClient, valid_request: dict, tmp_path: Path
) -> None:
    """The temporary file must be deleted by the route after sending to OCR."""
    fake_file = tmp_path / "to_delete.png"
    fake_file.write_bytes(b"\x89PNG")

    with patch(
        "ocr_backend.routers.v1.chat.retrieve_file_or_image_from_chat_message",
        return_value=fake_file,
    ):
        response = client.post(
            "/chat/completions",
            json=valid_request,
            headers={"Authorization": "Bearer secret-api"},
        )

    assert response.status_code == 200
    assert not fake_file.exists()


def test_chat_completion_streaming(client: TestClient, valid_request: dict) -> None:
    """stream=True: polls until done then streams OCR text word by word."""
    done_task = {
        **MOCK_TASK,
        "status": "done",
        "output": {
            "text": "Hello world",
            "type": "ocr",
            "model_name": "m",
            "created_at": 0,
            "updated_at": 0,
            "version": "1",
            "total_pages": 1,
            "pages": [],
        },
    }
    stream_request = {**valid_request, "stream": True}

    with patch(
        "ocr_backend.routers.v1.chat.get_latest_task_status",
        return_value=done_task,
    ):
        response = client.post(
            "/chat/completions",
            json=stream_request,
            headers={"Authorization": "Bearer secret-api"},
        )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    lines = [line for line in response.text.splitlines() if line.startswith("data:")]
    assert lines[-1] == "data: [DONE]"
    for line in lines[:-1]:
        chunk = json.loads(line[len("data: ") :])
        assert chunk["object"] == "chat.completion.chunk"
        assert chunk["model"] == "ocr-v1"


def test_chat_completion_streaming_error_task(client: TestClient, valid_request: dict) -> None:
    """stream=True: when task fails, streams [OCR failed] then [DONE]."""
    failed_task = {**MOCK_TASK, "status": "failed"}
    stream_request = {**valid_request, "stream": True}

    with patch(
        "ocr_backend.routers.v1.chat.get_latest_task_status",
        return_value=failed_task,
    ):
        response = client.post(
            "/chat/completions",
            json=stream_request,
            headers={"Authorization": "Bearer secret-api"},
        )

    assert response.status_code == 200
    lines = [line for line in response.text.splitlines() if line.startswith("data:")]
    assert lines[-1] == "data: [DONE]"
    chunks = [json.loads(line[len("data: ") :]) for line in lines[:-1]]
    content_chunks = [c for c in chunks if c["choices"][0]["delta"].get("content")]
    # On error the task JSON is streamed as content and finish_reason is "stop"
    assert len(content_chunks) == 1
    assert chunks[-1]["choices"][0]["finish_reason"] == "stop"
