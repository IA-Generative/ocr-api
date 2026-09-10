import io
import mimetypes
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
from urllib.parse import urlparse
from src.schemas.task import TaskModel, TaskUpdateForm, task_table, TaskStatus, TaskStats
from src.schemas.pagination import Pagination
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier
from datetime import datetime
from src.logger import logger
from ..connectors import s3_client_connector

router = APIRouter(tags=["Tasks"])


def _as_s3_key(page_url: str) -> str:
    """Normalise un ``page_url`` legacy (presigned URL complète, avant
    migration) en simple clé S3. Les tâches déjà migrées ont directement
    la clé stockée et sont retournées telles quelles."""
    if not page_url.startswith("http://") and not page_url.startswith("https://"):
        return page_url

    path = urlparse(page_url).path.lstrip("/")
    prefix = f"{s3_client_connector.bucket_name}/"
    if path.startswith(prefix):
        path = path[len(prefix) :]
    return path


def get_task_by_id(task_id: str) -> TaskModel:
    task = task_table.get_task_by_id(task_id)
    if task:
        task.position = task_table.get_position_in_queue(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != TaskStatus.COMPLETED.value:
        if task.output is not None:
            task.output.pages = []

    return task


@router.get(
    "/tasks/{task_id}",
    response_model=Optional[TaskModel],
    summary="Get a task by ID",
    description=(
        "Returns the task's current status/progress, and its full output once "
        "`status` is `completed`. Only the task's owner can read it."
    ),
    responses={404: {"description": "Task not found, or not owned by the caller"}},
)
async def get_task_by_id_user(
    task_id: str,
    ctx: RequestContext = Depends(TokenVerifier),
):
    task: TaskModel = get_task_by_id(task_id=task_id)
    if task.user_id != ctx.user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.get(
    "/tasks/{task_id}/page/{page_number}",
    summary="Download a page's rendered image",
    description="Streams the rendered image of one page (1-indexed) of a completed task's output.",
    responses={404: {"description": "Task, page, or stored image not found"}},
)
async def get_task_page(
    task_id: str,
    page_number: int,
    ctx: RequestContext = Depends(TokenVerifier),
) -> StreamingResponse:
    """Renvoie l'image d'une page (1-indexée) en la streamant depuis S3."""
    task: TaskModel = get_task_by_id(task_id=task_id)
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.output or not task.output.pages:
        raise HTTPException(status_code=404, detail="No result file available for this task")

    page_index = page_number - 1
    if not (0 <= page_index < len(task.output.pages)):
        raise HTTPException(status_code=404, detail=f"Page {page_number} not found for this task")

    page = task.output.pages[page_index]
    if not page.page_url:
        raise HTTPException(status_code=404, detail=f"Page {page_number} not found for this task")

    s3_key = _as_s3_key(page.page_url)
    if s3_key != page.page_url:
        # Migration à la volée : l'ancien format stockait la presigned URL
        # complète, on la remplace par la clé nue.
        task.output.pages[page_index].page_url = s3_key
        task_table.update_task(task_id=task_id, form_data=TaskUpdateForm(output=task.output))

    try:
        body = s3_client_connector.get_object_bytes(s3_key)
    except Exception:
        raise HTTPException(status_code=404, detail="Result file not found in storage")

    content_type = mimetypes.guess_type(s3_key)[0] or "application/octet-stream"
    extension = mimetypes.guess_extension(content_type) or ""
    filename = f"{task_id}_page_{page_number}{extension}"

    return StreamingResponse(
        io.BytesIO(body),
        media_type=content_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


def get_tasks_by_user_id(
    user_id: str, page: int = Query(1, ge=1), page_size: int = Query(10, le=100)
) -> Pagination[TaskModel]:
    count = task_table.count_tasks_by_user_id(user_id)
    tasks = task_table.get_tasks_by_user_id(user_id, page, page_size)
    if tasks is None or len(tasks) == 0:
        return Pagination[TaskModel](total=0, page=page, page_size=page_size, items=[])
    return Pagination[TaskModel](total=count, page=page, page_size=page_size, items=tasks)


@router.get(
    "/tasks/user/",
    response_model=Pagination[TaskModel],
    summary="List the caller's tasks",
    description="Paginated list of tasks created by the authenticated user.",
)
async def get_tasks_by_user(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    ctx: RequestContext = Depends(TokenVerifier),
):
    if ctx.user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_tasks_by_user_id(user_id=ctx.user_id, page=page, page_size=page_size)


@router.get(
    "/stats/tasks",
    response_model=TaskStats,
    summary="Get task statistics",
    description="Counts of tasks by status, both globally and for the authenticated user.",
)
async def get_tasks_stats(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    ctx: RequestContext = Depends(TokenVerifier),
):
    # reuse task_table.statistics which returns TaskStats
    # page and page_size are forwarded as skip/limit for admin listing
    skip = (page - 1) * page_size
    return task_table.statistics(user_id=ctx.user_id or "", is_admin=bool(ctx.is_admin), skip=skip, limit=page_size)


@router.get(
    "/users/count-users-today",
    summary="Count distinct active users today",
    description="Number of distinct users who created at least one task since midnight (server time).",
)
async def count_users_today(
    ctx: RequestContext = Depends(TokenVerifier),
):
    # count distinct users with tasks created today
    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day)
    start_ts = int(start_of_day.timestamp())
    end_ts = int(now.timestamp())
    count = task_table.count_unique_users_between_dates(start_ts, end_ts)
    return {"users_today": count}


@router.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="Delete a task",
    description="Deletes a task and its stored result. Only the task's owner or an admin can delete it.",
    responses={404: {"description": "Task not found, or not owned by the caller"}},
)
async def delete_task_by_id(
    task_id: str,
    ctx: RequestContext = Depends(TokenVerifier),
):
    task = get_task_by_id(task_id=task_id)
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=404, detail="Task not found")
    task_table.delete_task_by_id(task_id=task_id)
    try:
        s3_client_connector.delete_by_task_id(user_id=task.user_id, task_id=task.id)
    except Exception as e:
        logger.error(f"Error occurred while deleting task from S3: {e}")


@router.delete(
    "/v1/tasks/",
    status_code=204,
    summary="Bulk-delete tasks by date range and status (admin only)",
    description="Deletes every task created between `start_date` and `end_date` (inclusive) matching `status`.",
    responses={403: {"description": "Caller is not an admin"}},
)
async def delete_tasks_by_date_and_status(
    start_date: datetime,
    end_date: datetime,
    status: TaskStatus,
    ctx: RequestContext = Depends(TokenVerifier),
):
    if not ctx.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Only Admin users can delete tasks by date and status",
        )
    results = task_table.delete_tasks_by_date_and_status(start_date=start_date, end_date=end_date, status=status)
    if not results:
        return []

    for task in results:
        s3_client_connector.delete_by_task_id(user_id=task.user_id, task_id=task.id)
