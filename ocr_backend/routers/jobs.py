import json
import os
import shutil
import tempfile
import traceback

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.input import InputForm
from src.schemas.task import (
    TaskForm,
    TaskModel,
    TaskOperation,
    TaskStatus,
    TaskUpdateForm,
    task_table,
)


from ..connectors import s3_client_connector

router = APIRouter(tags=["Jobs"])


@router.post("/jobs/{user_id}", status_code=status.HTTP_201_CREATED, response_model=TaskModel)
async def upload_file(user_id: str, file: UploadFile = File(...)):
    extras = {}
    task_data = task_table.insert_new_task(
        user_id=user_id,
        form_data=TaskForm(
            user_id=user_id,
            type=TaskOperation.OCR.value,
            status=TaskStatus.CREATED.value,
            percentage=0.0,
            extras=extras,
        ),
    )
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name  # Le chemin du fichier temporaire
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        logger.debug(task_data.model_dump())

        saved_path = s3_client_connector.save(user_id, task_data.id, temp_file_path)
        logger.debug(f"Save into S3 - {saved_path}")

        _, extension = os.path.splitext(file.filename)

        extras = task_data.extras
        input_form = InputForm(
            storage_file_path=saved_path,
            raw_filename=os.path.basename(file.filename),
            content_type=file.content_type,
            ext=extension,
            size=file.size,
        )

        task_data = task_table.update_task(
            task_id=task_data.id,
            form_data=TaskUpdateForm(
                status=TaskStatus.QUEUED.value,
                input=input_form,
                extras=extras,
            ),
        )

        task_data.position = task_table.get_position_in_queue(task_id=task_data.id)
        os.remove(temp_file_path)

        celery_app.send_task(
            "worker.tasks.ocr",
            args=[json.dumps(task_data.model_dump())],
            task_id=task_data.id,
        )

        return task_data

    except Exception as e:
        logger.error(f"Failed to upload file for user {user_id}, task {task_data.id}: {e} - {traceback.format_exc()}")
        task_table.update_task(
            task_id=task_data.id,
            form_data=TaskUpdateForm(
                type=TaskOperation.OCR.value,
                status=TaskStatus.FAILED.value,
                extras={"error": str(e)},
            ),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload failed",
        )
