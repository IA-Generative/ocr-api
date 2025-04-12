import json
import tempfile
import shutil
import os
import traceback

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from ..clients import minio_connector, redis_client, redis_settings
from src.logger import logger
from src.schemas.task import task_table, TaskForm, TaskModel, TaskUpdateForm

router = APIRouter(tags=["Jobs"])


@router.post("/jobs/{user_id}", status_code=status.HTTP_201_CREATED, response_model=TaskModel)
async def upload_file(user_id: str, file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name  # Le chemin du fichier temporaire
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        task_data = task_table.insert_new_task(user_id=user_id, form_data=TaskForm(
            user_id=user_id, type="ocr", status="CREATED", percentage=0.0))

        logger.debug(task_data.model_dump())

        saved_path = minio_connector.save(
            user_id, task_data.id, temp_file_path)
        logger.debug(f'Save into minio - {saved_path}')

        _, extension = os.path.splitext(file.filename)

        task_data = task_table.update_task(task_id=task_data.id, form_data=TaskUpdateForm(
            status="pending", extras={"file_path": saved_path, "raw_filename": os.path.basename(file.filename),
                                      "content_type": file.content_type, "ext": extension}))

        os.remove(temp_file_path)

        redis_client.lpush(redis_settings.REDIS_QUEUE_NAME,
                           json.dumps(task_data.model_dump()))

        return task_data

    except Exception as e:
        logger.error(
            f"Failed to upload file for user {user_id}, task {task_data.id}: {e} - {traceback.format_exc()}")
        task_table.update_task(task_id=task_data.id, form_data=TaskUpdateForm(
            type="ocr", status="error", extras={"error": str(e)}))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed"
        )
