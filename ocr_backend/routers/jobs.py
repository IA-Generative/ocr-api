import json
import tempfile
import shutil
import os
import traceback

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from ..clients import minio_connector, redis_client, redis_settings
from src.logger import logger
from src.schemas.task import task_table, TaskForm, TaskModel, TaskUpdateForm, TaskStatus, TaskOperation

router = APIRouter(tags=["Jobs"])


@router.post(
    "/jobs/{user_id}", status_code=status.HTTP_201_CREATED, response_model=TaskModel
)
async def upload_file(user_id: str, file: UploadFile = File(...), extras: dict = None):
    if extras is None:
        extras = {}
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name  # Le chemin du fichier temporaire
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        task_data = task_table.insert_new_task(
            user_id=user_id,
            form_data=TaskForm(
                user_id=user_id, type=TaskOperation.OCR.value, status=TaskStatus.CREATED.value, percentage=0.0, extras=extras
            ),
        )

        logger.debug(task_data.model_dump())

        saved_path = minio_connector.save(
            user_id, task_data.id, temp_file_path)
        logger.debug(f"Save into minio - {saved_path}")

        _, extension = os.path.splitext(file.filename)

        extras = task_data.extras
        extras.update({
            "file_path": saved_path,
            "raw_filename": os.path.basename(file.filename),
            "content_type": file.content_type,
            "ext": extension,
        })

        task_data = task_table.update_task(
            task_id=task_data.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.QUEUED.value,
                extras=extras,
            ),
        )

        os.remove(temp_file_path)

        redis_client.lpush(
            redis_settings.REDIS_QUEUE_NAME, json.dumps(task_data.model_dump())
        )

        return task_data

    except Exception as e:
        logger.error(
            f"Failed to upload file for user {user_id}, task {task_data.id}: {e} - {traceback.format_exc()}"
        )
        task_table.update_task(
            task_id=task_data.id,
            form_data=TaskUpdateForm(
                type=TaskOperation.OCR.value, status=TaskStatus.FAILED.value, extras={
                    "error": str(e)}
            ),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed",
        )
