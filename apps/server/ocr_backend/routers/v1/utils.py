import tempfile
from pathlib import Path

import requests
from fastapi import HTTPException
from ocr_backend.connectors import s3_client_connector
from typing import Any
from src.logger import logger
from src.services.task_service import TaskService
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import ChatCompletionRequest
from src.schemas.task import (
    TaskForm,
    TaskModel,
    TaskUpdateForm,
    TaskStatus,
)

from src.schemas.input import InputForm
from src.connector.broker_connector import celery_app


ALLOWED_MIME_TYPES: list[str] = [
    "image/png",
    "image/jpeg",
    "application/pdf",
    "binary/octet-stream",
]

_MIME_TO_SUFFIX: dict[str, str] = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "application/pdf": ".pdf",
    "binary/octet-stream": "",  # No extension, will rely on original filename or content-based detection
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


async def aretrieve_from_private_s3(file_key: str) -> Path:
    """Async version — downloads from S3 without blocking the event loop."""
    data = await s3_client_connector.aget_object(file_key)
    suffix = Path(file_key).suffix
    return _write_to_tempfile(data, suffix=suffix)


def retrieve_from_url(
    url: str,
    mime_types_allowed: list[str] = ALLOWED_MIME_TYPES,
) -> Path:
    """Download a URL, enforce allowed MIME types, and return the path as a temporary file."""
    logger.debug(f"Downloading file from URL: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
    logger.debug(f"Content-Type of downloaded file: {content_type}")
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

    raise ValueError(f"No valid image URL or file data found in message content. {content}")


def retrieve_file_or_image_from_chat_message(message: ChatCompletionRequest) -> Path:
    """Extract the file from the first message and return it as a temporary Path.

    The caller is responsible for deleting the returned file when done.
    """
    if not message.messages:
        raise ValueError("No messages found in the chat completion request.")

    # Force serialization to plain dict to avoid getting pydantic ValidatorIterator
    # when content parts are typed as openai TypedDicts.
    first_message = message.model_dump()["messages"][0]
    content = first_message.get("content")
    if not content:
        raise ValueError("No content found in the first message.")

    return retrieve_file_or_image_from_message_content(content)  # type: ignore


async def sending_file_to_ocr_service(
    user_id: str,
    group_id: str,
    task_service: TaskService,
    db: AsyncSession,
    task_operation: str,
    file_path: Path,
    worker_name: str = "ocr",
) -> dict[str, Any]:
    """Simulate sending the file to an OCR service and getting back extracted text."""

    input_form = InputForm(
        storage_file_path=str(file_path),
        raw_filename=file_path.name,
        content_type="application/octet-stream",
        ext=file_path.suffix,
        size=file_path.stat().st_size,
        interest_zone=None,
    )

    task_data: TaskModel | None = await task_service.insert_new_task(
        db=db,
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
    logger.debug(f"Created new task with ID: {task_data.id if task_data else 'None'} for user_id: {user_id}")
    if not task_data:
        raise ValueError("Failed to create a new task in the database.")
    celery_app.send_task(
        name=worker_name,
        args=[task_data.model_dump()],
        task_id=task_data.id,
    )

    task_data = await task_service.update_task(
        db=db,
        task_type=task_operation,
        task_id=task_data.id,
        form_data=TaskUpdateForm(
            status=TaskStatus.QUEUED.value,
        ),
    )
    if not task_data:
        raise ValueError("Failed to update task status to QUEUED.")

    return task_data.model_dump()


async def get_latest_task_status(
    task_id: str, task_type: str, task_service: TaskService, db: AsyncSession
) -> dict[str, Any]:
    """Simulate retrieving the latest status of a task."""
    from src.schemas.task import TaskModel

    task_data: TaskModel | None = await task_service.get_task_by_id(db=db, task_id=task_id, task_type=task_type)
    if not task_data:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
    return task_data.model_dump()
