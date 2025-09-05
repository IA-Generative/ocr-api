from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from src.schemas.task import TaskModel, task_table, TaskStatus
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier
from datetime import datetime
from ..connectors import s3_client_connector

router = APIRouter(tags=["Tasks"])


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


@router.get("/tasks/{task_id}", response_model=Optional[TaskModel])
async def get_task_by_id_user(
    task_id: str,
    ctx: RequestContext = Depends(TokenVerifier),
):
    task: TaskModel = get_task_by_id(task_id=task_id)
    if task.user_id != ctx.user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


def get_tasks_by_user_id(
    user_id: str, page: int = Query(1, ge=1), page_size: int = Query(10, le=100)
) -> list[TaskModel]:
    tasks = task_table.get_tasks_by_user_id(user_id, page, page_size)
    if tasks is None or len(tasks) == 0:
        raise HTTPException(status_code=404, detail="No tasks found for this user")
    return tasks


@router.get(
    "/tasks/user/",
    response_model=List[TaskModel],
)
async def get_tasks_by_user(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    ctx: RequestContext = Depends(TokenVerifier),
):
    return get_tasks_by_user_id(user_id=ctx.user_id, page=page, page_size=page_size)


@router.delete("/v1/tasks/", response_model=Optional[list[TaskModel]])
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
    return results
