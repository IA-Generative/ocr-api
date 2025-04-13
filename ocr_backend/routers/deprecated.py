import json
import tempfile
import shutil
import os
import traceback
from typing import Optional
import asyncio

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from src.logger import logger
from ocr_backend.routers.jobs import upload_file, redis_client
from ocr_backend.routers.task import get_task_by_id
from src.schemas.task import TaskStatus, TaskModel

router = APIRouter(tags=["Older Routes"], prefix="/old")


@router.post("/", deprecated=True)
async def ocr(
    file: UploadFile = File(...),
    format: Optional[str] = None,
    max_height: Optional[int] = None,
    grayscale: Optional[bool] = True,
    return_image: Optional[bool] = True,
):
    task = await upload_file(user_id="unique", file=file, extras={
        "format": format,
        "max_height": max_height,
        "grayscale": grayscale,
        "return_image": return_image

    })
    while task.status not in [TaskStatus.CANCELED.value, TaskStatus.COMPLETED.value, TaskStatus.TIMEOUT.value]:
        task = await get_task_by_id(task_id=task.id)
        await asyncio.sleep(1)
        logger.debug(f"{task.id} - status : {task.status}")

    if task.status == TaskStatus.COMPLETED.value:
        task_data: bytes = redis_client.get(task.id)
        logger.debug(task_data)
        if task_data:
            return TaskModel(**json.loads(task_data.decode("utf-8")))

    return task
