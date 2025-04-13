import json
from typing import Optional
import asyncio
import time

from fastapi import APIRouter, File, UploadFile, HTTPException
from src.logger import logger
from ocr_backend.routers.jobs import upload_file, redis_client
from ocr_backend.routers.task import get_task_by_id
from src.schemas.task import TaskStatus, TaskModel
from src.schemas.box import Box

router = APIRouter(tags=["Older Routes"], prefix="/old")


@router.post("/", deprecated=True)
async def ocr(
    file: UploadFile = File(...),
    format: Optional[str] = None,
    max_height: Optional[int] = None,
    grayscale: Optional[bool] = True,
    return_image: Optional[bool] = True,
    user_id: Optional[str] = "ocr-user"
):
    time_to_upload = time.time()
    task = await upload_file(user_id=user_id, file=file, extras={
        "format": format,
        "max_height": max_height,
        "grayscale": grayscale,
        "return_image": return_image

    })
    logger.debug(f"{task.id} take {time.time() - time_to_upload}s to upload")

    while task.status not in [TaskStatus.CANCELED.value, TaskStatus.COMPLETED.value, TaskStatus.TIMEOUT.value]:
        task = await get_task_by_id(task_id=task.id)
        await asyncio.sleep(1)
        logger.debug(f"{task.id} - status : {task.status}")
    logger.debug(
        f"{task.id} take {task.updated_at - task.created_at}s to process")
    if task.status == TaskStatus.COMPLETED.value:
        task_data: bytes = redis_client.get(task.id)

        if task_data:
            task_result = TaskModel(**json.loads(task_data.decode("utf-8")))
            json_response = {"msg": "Success", "results": task_result.extras.get("results"),
                             "status": "200", "task_result": task_result.model_dump()}

            if return_image:
                json_response["images_base64"] = task_result.extras.get(
                    'images_base64')
            logger.debug(
                f"{task_result.id} take {time.time() - time_to_upload}s in total")
            return json_response

    logger.error(f"{task.id} got an error {task.extras}")

    raise HTTPException(status_code=500, detail=task.extras)


@router.post("/read")
async def read(ocr_data: list[list[Box]]):
    full_text = ""
    for page in ocr_data:
        # Sort each page by y1 (top position), then by x1 (left position)
        sorted_page = sorted(
            page,
            key=lambda item: (item.text_region[0][1], item.text_region[0][0]),
        )

        page_text = ""
        last_y = None
        # Threshold to decide whether two boxes are on the same line
        line_threshold = 10

        for item in sorted_page:
            text = item.text
            x1, y1 = item.text_region[0]  # top-left corner
            # y2 can be used if needed for more precise row checking

            # Add a new line if the current box starts a new row
            if last_y is not None and abs(y1 - last_y) > line_threshold:
                page_text += "\n"

            # Concatenate the current text to the output
            if page_text and page_text[-1] != "\n":
                page_text += " "  # Separate words with a space
            page_text += text

            # Update the last_y to the current box's y1
            last_y = y1

        # Append the concatenated text of the current page to the full text
        full_text += page_text + "\n\n"  # Separate pages with a double newline
    return full_text
