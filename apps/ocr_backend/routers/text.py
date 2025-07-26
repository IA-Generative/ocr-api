from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from src.schemas.task import task_table
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier


text_router = APIRouter(tags=["Text"])


@text_router.get("/text-task/{task_id}", response_class=PlainTextResponse, response_model=None)
async def download_text_content(task_id: str) -> PlainTextResponse:
    task = task_table.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    content = ""
    if task.output is not None:
        content = task.output.text

    return PlainTextResponse(content=content, status_code=200, media_type="text/plain")


@text_router.get("/v1/text-task/{task_id}", response_class=PlainTextResponse, response_model=None)
async def download_text_content_new(
    task_id: str,
    ctx: RequestContext = Depends(TokenVerifier),
) -> PlainTextResponse:
    task = task_table.get_task_by_id(task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != ctx.user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    content = ""
    if task.output is not None:
        content = task.output.text

    return PlainTextResponse(content=content, status_code=200, media_type="text/plain")
