from fastapi import APIRouter, File, UploadFile, HTTPException, status
from typing import Optional
from uuid import uuid4
import tempfile
import shutil
import os
from ..clients import minio_connector
from src.logger import logger
from src.schemas.task import task_table, TaskForm, TaskModel

router = APIRouter(tags=["Jobs"])


@router.post("/jobs/{user_id}", status_code=status.HTTP_201_CREATED, response_model=TaskModel)
async def upload_file(user_id: str, file: UploadFile = File(...)):
    try:
        task_id = str(uuid4())

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name  # Le chemin du fichier temporaire
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        saved_path = minio_connector.save(user_id, task_id, temp_file_path)

        os.remove(temp_file_path)

        return task_table.insert_new_task(user_id=user_id, form_data=TaskForm(user_id=user_id, type="ocr", status="pending", percentage=0.0,
                                                                              extras={"file_path": saved_path, }))

    except Exception as e:
        logger.error(
            f"Failed to upload file for user {user_id}, task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed"
        )
