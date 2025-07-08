from fastapi import APIRouter, HTTPException, Query, Depends
import warnings
from typing import List, Optional
from src.schemas.task import TaskModel, task_table
from ocr_backend.core.token import RequestContext
from ocr_backend.core.factory import TokenVerifier

router = APIRouter(tags=["Tasks"])


@router.get("/tasks/{task_id}/old", response_model=Optional[TaskModel])
async def get_task_by_id(task_id: str):
    warnings.warn(
        message="get_task_by_id will be deprecated in next version use instead ",
        category=DeprecationWarning,
        stacklevel=2,
    )
    task = task_table.get_task_by_id(task_id)
    if task:
        task.position = task_table.get_position_in_queue(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.get("/tasks/{task_id}", response_model=Optional[TaskModel])
async def get_task_by_id_user(
    task_id: str,
    ctx: RequestContext = Depends(TokenVerifier),
):
    task: TaskModel = await get_task_by_id(task_id=task_id)
    if task.user_id != ctx.user_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.get(
    "/tasks/user/{user_id}",
    response_model=List[TaskModel],
)
async def get_tasks_by_user_id(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
):
    warnings.warn(
        message="get_tasks_by_user_id will be deprecated in next version use instead get_tasks_by_user",
        category=DeprecationWarning,
        stacklevel=2,
    )
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
    print(ctx)
    print(79 * "*")

    return await get_tasks_by_user_id(user_id=ctx.user_id, page=page, page_size=page_size)
