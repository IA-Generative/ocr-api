import json
from json import JSONDecodeError
import os
import aiofiles
import traceback
from typing import Optional, Annotated, AsyncGenerator

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
    Depends,
    Form,
)
import fitz

from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.input import InputForm, RegionOfInterest
from src.schemas.task import (
    TaskForm,
    TaskModel,
    TaskOperation,
    TaskStatus,
    TaskUpdateForm,
    CeleryTaskName,
)
from celery import chain, group
from src.services.task_service import TaskService
from src.connector.db_connector import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier

from ..connectors import s3_client_connector

router = APIRouter(tags=["Jobs"])
TokenDep = Annotated[RequestContext, Depends(TokenVerifier)]
TaskServiceDep = Annotated[TaskService, Depends(TaskService)]


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dépendance pour obtenir une session async"""
    async with AsyncSessionLocal() as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def _handle_pdf_interest_zone(file_path: str, interest_zone: Optional[str]) -> list[RegionOfInterest]:
    doc = fitz.open(file_path)
    if doc.is_form_pdf:
        return []
    try:
        regions = [RegionOfInterest(**item) for item in json.loads(interest_zone)]
        if len(regions) != len(doc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Interest zone cannot be empty for PDF files {traceback.format_exc()}",
            )
        return regions
    except JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format for interest_zone {e}{traceback.format_exc()}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format for interest_zone {e}{traceback.format_exc()}",
        )


def _handle_image_interest_zone(interest_zone: Optional[str]) -> list[RegionOfInterest]:
    regions = [RegionOfInterest(**item) for item in json.loads(interest_zone)]
    if len(regions) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Interest zone cannot be empty for image files {traceback.format_exc()}",
        )
    return regions


def verify_interest_zone(
    file_path: str,
    content_type: str,
    interest_zone: Optional[str] = "",
) -> list[RegionOfInterest]:
    if content_type == "application/pdf":
        return _handle_pdf_interest_zone(file_path, interest_zone)
    elif content_type.startswith("image/"):
        return _handle_image_interest_zone(interest_zone)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type {traceback.format_exc()}",
        )


@router.post("/jobs/", status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: Annotated[UploadFile, File(...)],
    ctx: TokenDep,
    task_service: TaskServiceDep,
    db_session: DbSessionDep,
    group_id: Annotated[str, Form()] = "DEFAULT",
    parameter: Annotated[Optional[str], Form()] = None,
    task_operation: Annotated[TaskOperation, Form()] = TaskOperation.DEFAULT,
    task_name: Annotated[Optional[CeleryTaskName], Form()] = CeleryTaskName.OCR_TASK,
) -> TaskModel:
    if ctx.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    parameter_dict = {}
    if parameter:
        try:
            parameter_dict = json.loads(parameter)
        except JSONDecodeError as e:
            logger.error(
                f"HTTPException for user {ctx.user_id}: Invalid JSON in parameter - {e} - {traceback.format_exc()}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON format for parameter: {e} {traceback.format_exc()}",
            )
    extras = {}
    task_data = await task_service.insert_new_task(
        db=db_session,
        user_id=ctx.user_id,
        form_data=TaskForm(
            type=CeleryTaskName.OCR_TASK.value,
            status=TaskStatus.CREATED.value,
            percentage=0.0,
            extras=extras,
            group_id=group_id,
            parameters=parameter_dict,
        ),
    )
    try:
        async with aiofiles.tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

            # Lecture par chunks pour économiser la mémoire
            chunk_size = 8192  # 8KB chunks
            while chunk := await file.read(chunk_size):
                await temp_file.write(chunk)

    except Exception as e:
        logger.error(f"HTTPException for user {ctx.user_id}, task {task_data.id}: {e} - {traceback.format_exc()}")
        await task_service.update_task(
            db=db_session,
            task_id=task_data.id,
            task_type=CeleryTaskName.OCR_TASK.value,
            form_data=TaskUpdateForm(
                type=CeleryTaskName.OCR_TASK.value,
                status=TaskStatus.FAILED.value,
                extras={"error": str(e)},
            ),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON format for interest_zone {e}{traceback.format_exc()}",
        )

    try:
        saved_path = await s3_client_connector.asave(ctx.user_id, task_data.id, temp_file_path)
        logger.debug(f"Save into S3 - {saved_path}")

        _, extension = os.path.splitext(file.filename)
        extras = task_data.extras
        input_form = InputForm(
            storage_file_path=saved_path,
            raw_filename=os.path.basename(file.filename),
            content_type=file.content_type,
            ext=extension,
            size=file.size if file.size is not None else 0,
            parameters=parameter_dict,
        )

        task_data = await task_service.update_task(
            db=db_session,
            task_id=task_data.id,
            task_type=CeleryTaskName.OCR_TASK.value,
            form_data=TaskUpdateForm(
                status=TaskStatus.QUEUED.value,
                input=input_form,
                extras=extras,
            ),
        )

        task_data.position = await task_service.get_position_in_queue(
            db=db_session, task_id=task_data.id, task_type=CeleryTaskName.OCR_TASK.value
        )
        os.remove(temp_file_path)

        ocr_sig = celery_app.signature(
            CeleryTaskName.OCR_TASK.value,
            args=[task_data.model_dump()],
            task_id=str(task_data.id),
        )
        ocr_chunk_sig = celery_app.signature(CeleryTaskName.OCR_CHUNK_TASK.value)

        if task_name and task_name == CeleryTaskName.PAGE_TEXT_CLASSIFICATION_TASK:
            # Classification et chunk en parallèle après l'OCR
            classification_sig = celery_app.signature(task_name.value)
            chain(ocr_sig, group(ocr_chunk_sig, classification_sig)).apply_async()
        elif task_name and task_name not in (
            CeleryTaskName.OCR_TASK,
            CeleryTaskName.OCR_CHUNK_TASK,
        ):
            # Entity extraction (ou autre) dépend du chunk
            chain(ocr_sig, ocr_chunk_sig, celery_app.signature(task_name.value)).apply_async()
        elif task_name and task_name == CeleryTaskName.OCR_TASK_ONLY:
            # OCR seul → pas de chunk
            chain(ocr_sig).apply_async()
        else:
            # OCR seul → toujours suivi du chunk
            chain(ocr_sig, ocr_chunk_sig).apply_async()

        return task_data

    except Exception as e:
        logger.error(
            f"Failed to upload file for user {ctx.user_id}, task {task_data.id}: {e} - {traceback.format_exc()}"
        )
        await task_service.update_task(
            db=db_session,
            task_id=task_data.id,
            task_type=CeleryTaskName.OCR_TASK.value,
            form_data=TaskUpdateForm(
                type=CeleryTaskName.OCR_TASK.value,
                status=TaskStatus.FAILED.value,
                extras={"error": str(e)},
            ),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {e} {traceback.format_exc()}",
        )
