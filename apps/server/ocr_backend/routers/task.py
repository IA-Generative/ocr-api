from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, Optional
from src.schemas.task import (
    TaskModel,
    task_table,
    TaskStatus,
    TaskStats,
    TaskUpdateForm,
)
from src.schemas.pagination import Pagination
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier
from datetime import datetime
from src.logger import logger
from ..connectors import s3_client_connector

router = APIRouter(tags=["Tasks"])

TokenDep = Annotated[RequestContext, Depends(TokenVerifier)]
PageDep = Annotated[int, Query(ge=1)]
PageSizeDep = Annotated[int, Query(le=100)]


def _rewrite_page_urls(task: TaskModel) -> TaskModel:
    """Replace the origin of page_url with the public URL, regardless of the internal hostname."""
    if task.output and task.output.pages:
        for page in task.output.pages:
            if page.page_url:
                # Avoid generating a presigned URL if `page_url` is already a full URL
                if not (page.page_url.startswith("http://") or page.page_url.startswith("https://")):
                    page.page_url = s3_client_connector.generate_presigned_url(page.page_url)
    return task


def get_task_by_id(task_id: str) -> TaskModel:
    task = task_table.get_task_by_id(task_id)
    if task:
        task.position = task_table.get_position_in_queue(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status != TaskStatus.COMPLETED.value:
        if task.output is not None:
            task.output.pages = []

    return _rewrite_page_urls(task)


@router.get("/tasks/{task_id}", response_model=Optional[TaskModel])
async def get_task_by_id_user(
    task_id: str,
    ctx: TokenDep,
):
    task: TaskModel = get_task_by_id(task_id=task_id)
    if task.user_id != ctx.user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.patch("/tasks/{task_id}", response_model=TaskModel)
async def update_task_status(
    task_id: str,
    update_form: TaskUpdateForm,
    ctx: TokenDep,
):
    task: TaskModel = get_task_by_id(task_id=task_id)
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=404, detail="Task not found")
    task_table.update_task(task_id=task_id, form_data=update_form)
    task: TaskModel = get_task_by_id(task_id=task_id)
    return task


def get_tasks_by_user_id(user_id: str, page: int = 1, page_size: int = 10) -> Pagination[TaskModel]:
    count = task_table.count_tasks_by_user_id(user_id)
    tasks = task_table.get_tasks_by_user_id(user_id, page, page_size)
    if tasks is None or len(tasks) == 0:
        return Pagination[TaskModel](total=0, page=page, page_size=page_size, items=[])
    return Pagination[TaskModel](total=count, page=page, page_size=page_size, items=tasks)


@router.get(
    "/tasks/user/",
    response_model=Pagination[TaskModel],
)
async def get_tasks_by_user(
    ctx: TokenDep,
    page: PageDep = 1,
    page_size: PageSizeDep = 10,
):
    if ctx.user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return get_tasks_by_user_id(user_id=ctx.user_id, page=page, page_size=page_size)


@router.get(
    "/stats/tasks",
    response_model=TaskStats,
)
async def get_tasks_stats(
    ctx: TokenDep,
    page: PageDep = 1,
    page_size: PageSizeDep = 10,
):
    # reuse task_table.statistics which returns TaskStats
    # page and page_size are forwarded as skip/limit for admin listing
    skip = (page - 1) * page_size
    return task_table.statistics(
        user_id=ctx.user_id or "",
        is_admin=bool(ctx.is_admin),
        skip=skip,
        limit=page_size,
    )


@router.get("/users/count-users-today")
async def count_users_today(
    ctx: TokenDep,
):
    # count distinct users with tasks created today
    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day)
    start_ts = int(start_of_day.timestamp())
    end_ts = int(now.timestamp())
    count = task_table.count_unique_users_between_dates(start_ts, end_ts)
    return {"users_today": count}


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task_by_id(
    task_id: str,
    ctx: TokenDep,
):
    task = get_task_by_id(task_id=task_id)
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=404, detail="Task not found")
    task_table.delete_task_by_id(task_id=task_id)
    try:
        s3_client_connector.delete_by_task_id(user_id=task.user_id, task_id=task.id)
    except Exception as e:
        logger.error(f"Error occurred while deleting task from S3: {e}")


@router.delete("/v1/tasks/", status_code=204)
async def delete_tasks_by_date_and_status(
    start_date: datetime,
    end_date: datetime,
    status: TaskStatus,
    ctx: TokenDep,
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
