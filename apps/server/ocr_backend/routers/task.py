from fastapi import APIRouter, HTTPException, Query, Depends, status as http_status
from typing import Optional, Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.task import (
    TaskModel,
    TaskStatus,
    TaskStats,
    TaskOperation,
    TaskUpdateForm,
    TaskForm,
)
from src.services.task_service import TaskService
from src.schemas.pagination import Pagination
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier
from datetime import datetime
from src.logger import logger
from ..connectors import s3_client_connector
from src.connector.db_connector import AsyncSessionLocal

router = APIRouter(tags=["Tasks"])

TokenDep = Annotated[RequestContext, Depends(TokenVerifier)]
PageDep = Annotated[int, Query(ge=1)]
PageSizeDep = Annotated[int, Query(le=100)]


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dépendance pour obtenir une session async"""
    async with AsyncSessionLocal() as session:
        yield session


def get_task_service() -> TaskService:
    """Dépendance pour obtenir une instance de TaskService"""
    return TaskService()


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def _rewrite_page_urls(task: TaskModel) -> TaskModel:
    """Replace the origin of page_url with the public URL, regardless of the internal hostname."""
    if task.output and task.output.pages:
        for page in task.output.pages:
            if page.page_url:
                # Avoid generating a presigned URL if `page_url` is already a full URL
                logger.debug(f"Original page URL: {page.page_url}")
                key = page.page_url
                if page.page_url.startswith("http://") or page.page_url.startswith("https://"):
                    logger.debug("Page URL is already a full URL, skipping presigned URL generation.")
                    key = s3_client_connector.extract_key_from_url(
                        page.page_url,
                        bucket_name=s3_client_connector.bucket_name,
                        s3_endpoint=s3_client_connector.client.meta.endpoint_url,
                    )
                    # TODO: save the extracted key back to the database to avoid this step in the future

                page.page_url = s3_client_connector.generate_presigned_url(
                    key,
                    expires_in=300,  # URL valable 5 minutes
                )
    return task


async def get_task_by_id_internal(task_id: str, db: AsyncSession, task_service: TaskService) -> TaskModel:
    """Helper interne pour récupérer une tâche avec enrichissement"""
    # Récupérer toutes les tâches avec cet ID
    tasks = await task_service.get_tasks_by_id(db, task_id)
    if not tasks:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    task = tasks[0]  # Prendre la première tâche

    # Récupérer la position en file d'attente
    if task.status == TaskStatus.QUEUED.value:
        position = await task_service.get_position_in_queue(db, task.id, task.type)
        task.position = position

    # Ne pas retourner les pages sauf si complète
    if task.status != TaskStatus.COMPLETED.value:
        if task.output is not None:
            task.output.pages = []

    return _rewrite_page_urls(task)


@router.post("/tasks", response_model=TaskModel, status_code=http_status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskForm,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
):
    """Crée une nouvelle tâche"""
    if ctx.user_id is None:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    new_task = await task_service.insert_new_task(
        db=db,
        user_id=ctx.user_id,
        form_data=task_data,
    )
    return new_task


@router.get("/tasks/{task_id}", response_model=Optional[TaskModel])
async def get_task_by_id_user(
    task_id: str,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
    task_type: Optional[TaskOperation] = None,
):
    """Récupère une tâche par son ID (utilisateur)"""
    if not task_type:
        logger.warning(
            f"Task type not provided for task_id {task_id}, fetching all tasks with this ID to find the correct one."
        )
        task = await get_task_by_id_internal(task_id, db, task_service)
    else:
        logger.debug(f"Fetching task with ID {task_id} and type {task_type}.")
        task = await task_service.get_task_by_id(db, task_id, task_type)
    if task is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != ctx.user_id and not ctx.is_admin:
        logger.warning(
            f"User {ctx.user_id} attempted to access task {task_id} owned by {task.user_id} without permission."
        )
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task


@router.get("/tasks/content/{content_hash}", response_model=Optional[TaskModel])
async def get_task_by_content_hash(
    content_hash: str,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
):
    """Récupère une tâche par son hash de contenu (utilisateur)"""

    logger.warning(
        f"Task type not provided for content_hash {content_hash}, fetching all tasks with this hash to find the correct one."
    )
    task = await task_service.get_task_by_content_hash(
        db,
        content_hash,
    )

    if task is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != ctx.user_id and not ctx.is_admin:
        logger.warning(
            f"User {ctx.user_id} attempted to access task with content_hash {content_hash} owned by {task.user_id} without permission."
        )
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task


@router.patch("/tasks/{task_id}", response_model=TaskModel)
async def update_task_by_id(
    task_id: str,
    task_type: TaskOperation,
    update_data: TaskUpdateForm,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
):
    """Met à jour une tâche par son ID (utilisateur)"""
    task = await task_service.get_task_by_id(db, task_id, task_type)
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    updated_task = await task_service.update_task(db, task_id, task_type, form_data=update_data)
    return _rewrite_page_urls(updated_task)


@router.get(
    "/tasks/user/",
    response_model=Pagination[TaskModel],
)
async def get_tasks_by_user(
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
    page: PageDep = 1,
    page_size: PageSizeDep = 10,
):
    """Récupère les tâches d'un utilisateur avec pagination"""
    if ctx.user_id is None:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    count = await task_service.count_tasks_by_user_id(db, ctx.user_id)
    tasks = await task_service.get_tasks_by_user_id(db, ctx.user_id, page, page_size)

    if tasks is None or len(tasks) == 0:
        return Pagination[TaskModel](total=0, page=page, page_size=page_size, items=[])

    return Pagination[TaskModel](total=count, page=page, page_size=page_size, items=tasks)


@router.get(
    "/stats/tasks",
    response_model=TaskStats,
)
async def get_tasks_stats(
    db: DbSessionDep,
    task_service: TaskServiceDep,
    ctx: TokenDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
):
    """Récupère les statistiques des tâches"""
    skip = (page - 1) * page_size
    return await task_service.statistics(
        db,
        user_id=ctx.user_id or "",
        is_admin=bool(ctx.is_admin),
        skip=skip,
        limit=page_size,
    )


@router.get("/users/count-users-today")
async def count_users_today(
    db: DbSessionDep,
    task_service: TaskServiceDep,
    ctx: TokenDep,
):
    """Compte le nombre d'utilisateurs uniques avec des tâches aujourd'hui"""
    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day)
    start_ts = int(start_of_day.timestamp())
    end_ts = int(now.timestamp())

    count = await task_service.count_unique_users_between_dates(db, start_ts, end_ts)
    return {"users_today": count}


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task_by_id(
    task_id: str,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
):
    """Supprime une tâche"""
    task = await get_task_by_id_internal(task_id, db, task_service)
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    await task_service.delete_task_by_id(db, task.id, task.type)

    try:
        s3_client_connector.delete_by_task_id(user_id=task.user_id, task_id=task.id)
    except Exception as e:
        logger.error(f"Error occurred while deleting task from S3: {e}")


@router.delete("/v1/tasks/", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_tasks_by_date_and_status(
    start_date: datetime,
    end_date: datetime,
    status: TaskStatus,
    db: DbSessionDep,
    task_service: TaskServiceDep,
    ctx: TokenDep,
):
    """Supprime les tâches avec un statut donné dans une plage de dates (admin)"""
    if not ctx.is_admin:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only Admin users can delete tasks by date and status",
        )

    results = await task_service.delete_tasks_by_date_and_status(
        db, start_date=start_date, end_date=end_date, status=status
    )

    if not results:
        return []

    for task in results:
        try:
            s3_client_connector.delete_by_task_id(user_id=task.user_id, task_id=task.id)
        except Exception as e:
            logger.error(f"Error occurred while deleting task from S3: {e}")
