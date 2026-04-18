from typing import Literal, Annotated, AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends, status as http_status
from fastapi.responses import PlainTextResponse, Response
from src.services.task_service import TaskService
from src.connector.db_connector import AsyncSessionLocal
from src.schemas.task import TaskOperation
from sqlalchemy.ext.asyncio import AsyncSession
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier
import io
import csv


text_router = APIRouter(tags=["Text"])
TokenDep = Annotated[RequestContext, Depends(TokenVerifier)]
TaskServiceDep = Annotated[TaskService, Depends(TaskService)]


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


@text_router.get("/text-task/{task_id}", response_class=PlainTextResponse, response_model=None)
async def download_text_content_new(
    task_id: str,
    ctx: TokenDep,
    task_service: TaskServiceDep,
    db_session: DbSessionDep,
    task_type: TaskOperation = TaskOperation.OCR,
) -> PlainTextResponse:
    task = await task_service.get_task_by_id(task_id=task_id, db=db_session, task_type=task_type)

    if task is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != ctx.user_id:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    content = ""
    if task.output is not None:
        content = task.output.text

    return PlainTextResponse(content=content, status_code=200, media_type="text/plain")


@text_router.get(
    "/task-to-value/{task_id}",
    response_model=None,
)
async def download_task_form(
    task_id: str,
    ctx: TokenDep,
    task_service: TaskServiceDep,
    db_session: DbSessionDep,
    transform: Literal["text", "form", "form-csv", "only-result"] = "text",
    task_type: TaskOperation = TaskOperation.OCR,
):
    task = await task_service.get_task_by_id(task_id=task_id, db=db_session, task_type=task_type)

    if task is None or task.user_id != ctx.user_id:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    if task.output is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task output not found")

    if transform == "text":
        return PlainTextResponse(content=task.output.text, status_code=200, media_type="text/plain")

    if transform == "only-result":
        return task.output

    pages = task.output.pages

    if transform == "form":
        return [page.form_entries for page in pages]

    if transform == "form-csv":
        output = io.StringIO()
        writer = None
        wrote_header = False
        for page in pages:
            entries = [entry.model_dump() for entry in page.form_entries]
            if entries:
                if writer is None:
                    writer = csv.DictWriter(output, fieldnames=entries[0].keys())
                if not wrote_header:
                    writer.writeheader()
                    wrote_header = True
                writer.writerows(entries)
        content = output.getvalue()
        output.close()
        # Si pas d'entrée, on retourne un CSV vide avec juste l'en-tête
        if not content:
            content = ""
        filename = f"{task.input.raw_filename}.csv" if task.input and task.input.raw_filename else "output.csv"
        return Response(
            content=content,
            status_code=200,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
