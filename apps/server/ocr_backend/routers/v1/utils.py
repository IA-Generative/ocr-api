import tempfile
from pathlib import Path

import requests
from fastapi import HTTPException
from ocr_backend.connectors import s3_client_connector
from typing import Any

from .schemas import ChatCompletionRequest

ALLOWED_MIME_TYPES: list[str] = ["image/png", "image/jpeg", "application/pdf"]

_MIME_TO_SUFFIX: dict[str, str] = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "application/pdf": ".pdf",
}


def _write_to_tempfile(data: bytes, suffix: str = "") -> Path:
    """Write bytes to a named temporary file and return its Path.

    The file is NOT deleted on close so the caller can use and then delete it.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        return Path(tmp.name)


def retrieve_from_private_s3(file_key: str) -> Path:
    """Download a file from S3 and return its path as a temporary file."""
    data: bytes = s3_client_connector.client.get_object(Bucket=s3_client_connector.bucket_name, Key=file_key)[
        "Body"
    ].read()
    suffix = Path(file_key).suffix
    return _write_to_tempfile(data, suffix=suffix)


def retrieve_from_url(
    url: str,
    mime_types_allowed: list[str] = ALLOWED_MIME_TYPES,
) -> Path:
    """Download a URL, enforce allowed MIME types, and return the path as a temporary file."""
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
    if content_type not in mime_types_allowed:
        raise ValueError(f"Unsupported MIME type '{content_type}'. Allowed: {', '.join(mime_types_allowed)}")

    suffix = _MIME_TO_SUFFIX.get(content_type, "")
    return _write_to_tempfile(response.content, suffix=suffix)


def retrieve_file_or_image_from_message_content(
    content: list[dict],
) -> Path:
    """Extract the file from a message content list and return it as a temporary Path.

    Resolution order for each part:
    - ``image_url``: download via HTTP (MIME type validated).
    - ``file`` with ``file_id``: treat as an S3 key and download from the
      private bucket.
    - ``file`` with ``file_data``: decode the base-64 payload directly.

    The caller is responsible for deleting the returned file when done.
    """
    for part in content:
        if not isinstance(part, dict):
            continue

        if part.get("type") == "image_url":
            url = part.get("image_url", {}).get("url")
            if url:
                return retrieve_from_url(url)

        elif part.get("type") == "file":
            file_info = part.get("file", {})

            file_id = file_info.get("file_id")
            if file_id:
                return retrieve_from_private_s3(file_id)

            file_data = file_info.get("file_data")
            if file_data:
                if file_data.startswith(("http://", "https://")):
                    return retrieve_from_url(file_data)
                else:
                    return retrieve_from_private_s3(file_data)

    raise ValueError("No valid image URL or file data found in message content.")


def retrieve_file_or_image_from_chat_message(message: ChatCompletionRequest) -> Path:
    """Extract the file from the first message and return it as a temporary Path.

    The caller is responsible for deleting the returned file when done.
    """
    if not message.messages:
        raise ValueError("No messages found in the chat completion request.")

    content = message.messages[0].get("content")
    if not content:
        raise ValueError("No content found in the first message.")

    return retrieve_file_or_image_from_message_content(content)  # type: ignore


def sending_file_to_ocr_service(
    user_id: str,
    group_id: str,
    task_operation: str,
    file_path: Path,
    worker_name: str = "ocr",
) -> dict[str, Any]:
    """Simulate sending the file to an OCR service and getting back extracted text."""
    from src.schemas.task import (
        TaskForm,
        TaskModel,
        TaskUpdateForm,
        TaskStatus,
        task_table,
    )
    from src.schemas.input import InputForm
    from src.connector.broker_connector import celery_app

    input_form = InputForm(
        storage_file_path=str(file_path),
        raw_filename=file_path.name,
        content_type="application/octet-stream",
        ext=file_path.suffix,
        size=file_path.stat().st_size,
        interest_zone=None,
    )

    task_data: TaskModel | None = task_table.insert_new_task(
        user_id=user_id,
        form_data=TaskForm(
            type=task_operation,
            status=TaskStatus.CREATED.value,
            percentage=0.0,
            input=input_form,
            extras={},
            group_id=group_id,
        ),
    )
    if not task_data:
        raise ValueError("Failed to create a new task in the database.")
    celery_app.send_task(
        name=worker_name,
        args=[task_data.model_dump()],
        task_id=task_data.id,
    )

    task_data = task_table.update_task(
        task_id=task_data.id,
        form_data=TaskUpdateForm(
            status=TaskStatus.QUEUED.value,
        ),
    )
    if not task_data:
        raise ValueError("Failed to update task status to QUEUED.")

    return task_data.model_dump()


def get_latest_task_status(task_id: str) -> dict[str, Any]:
    """Simulate retrieving the latest status of a task."""
    from src.schemas.task import TaskModel, task_table

    task_data: TaskModel | None = task_table.get_task_by_id(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
    return task_data.model_dump()
