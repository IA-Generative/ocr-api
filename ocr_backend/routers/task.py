from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from src.schemas.task import TaskTable, TaskModel

task_table = TaskTable()

router = APIRouter(tags=["Tasks"])


@router.get("/tasks/{task_id}", response_model=Optional[TaskModel])
async def get_task_by_id(task_id: str):
    task = task_table.get_task_by_id(task_id)
    task.position = task_table.get_position_in_queue(task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks/user/{user_id}", response_model=List[TaskModel])
async def get_tasks_by_user_id(
    user_id: str, page: int = Query(1, ge=1), page_size: int = Query(10, le=100)
):
    tasks = task_table.get_tasks_by_user_id(user_id, page, page_size)
    if tasks is None or len(tasks) == 0:
        raise HTTPException(status_code=404, detail="No tasks found for this user")
    return tasks
