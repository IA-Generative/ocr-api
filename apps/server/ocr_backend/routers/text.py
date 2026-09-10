from typing import Literal
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import PlainTextResponse, Response
from src.schemas.task import task_table
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier
import io
import csv


text_router = APIRouter(tags=["Text"])


@text_router.get(
    "/text-task/{task_id}",
    response_class=PlainTextResponse,
    response_model=None,
    summary="Get a task's extracted text",
    description="Plain-text extraction result of a task (empty string if not yet completed).",
    responses={404: {"description": "Task not found, or not owned by the caller"}},
)
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
        # OCRResult a `.text`, AudioTranscriptionResult a `.transcription_text`.
        content = getattr(task.output, "text", None) or getattr(task.output, "transcription_text", None) or ""

    return PlainTextResponse(content=content, status_code=200, media_type="text/plain")


@text_router.get(
    "/task-to-value/{task_id}",
    response_model=None,
    summary="Get a task's output in a chosen shape",
    description=(
        "Returns a completed task's output transformed for a specific use case, "
        "selected via `transform`:\n\n"
        "- `text` (default): plain extracted text\n"
        "- `form`: list of per-page extracted form entries (JSON)\n"
        "- `form-csv`: form entries as a downloadable CSV file\n"
        "- `only-result`: the raw OCR result object (JSON)"
    ),
    responses={404: {"description": "Task, or its output, not found (or not owned by the caller)"}},
)
async def download_task_form(
    task_id: str,
    transform: Literal["text", "form", "form-csv", "only-result"] = "text",
    ctx: RequestContext = Depends(TokenVerifier),
):
    task = task_table.get_task_by_id(task_id)

    if task is None or task.user_id != ctx.user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.output is None:
        raise HTTPException(status_code=404, detail="Task output not found")

    if transform == "text":
        content = getattr(task.output, "text", None) or getattr(task.output, "transcription_text", None) or ""
        return PlainTextResponse(content=content, status_code=200, media_type="text/plain")

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
        return Response(
            content=content,
            status_code=200,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{task.input.raw_filename}.csv"'},
        )
