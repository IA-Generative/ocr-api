from fastapi import APIRouter, HTTPException, Query, Depends, status as http_status
from fastapi.responses import StreamingResponse
from typing import Optional, Annotated, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import io
from src.schemas.task import (
    TaskModel,
    TaskStatus,
    TaskStats,
    TaskOperation,
    TaskUpdateForm,
    TaskForm,
    CeleryTaskName,
    LeaderboardResponse,
)
from src.services.task_service import TaskService
from src.schemas.pagination import Pagination
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier
from datetime import datetime
from src.logger import logger
from ..connectors import s3_client_connector
from src.connector.db_connector import AsyncSessionLocal
from src.connector.broker_connector import celery_app

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


def normalize_page_url(page_url: str) -> str:
    """Normalize the page URL by extracting the S3 key if it's a full URL."""
    if page_url.startswith("http://") or page_url.startswith("https://"):
        return s3_client_connector.extract_key_from_url(
            page_url,
            bucket_name=s3_client_connector.bucket_name,
            s3_endpoint=s3_client_connector.client.meta.endpoint_url,
        )
    return page_url


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

                page.page_url = key
    return task


async def _rewrite_page_urls_async(task: TaskModel) -> TaskModel:
    """Non-blocking wrapper around _rewrite_page_urls to avoid blocking the event loop."""
    if task.output and task.output.pages:
        return await asyncio.to_thread(_rewrite_page_urls, task)
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

    return await _rewrite_page_urls_async(task)


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
    # Always use get_task_by_id_internal — it does a PK lookup (fast),
    # plus position-in-queue and presigned-URL enrichment that the client needs.
    task = await get_task_by_id_internal(task_id, db, task_service)
    if task is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != ctx.user_id and not ctx.is_admin:
        logger.warning(
            f"User {ctx.user_id} attempted to access task {task_id} owned by {task.user_id} without permission."
        )
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task


@router.get("/tasks/{task_id}/result-file")
async def download_task_result_file(
    task_id: str,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
):
    """Télécharge le fichier résultat (document rempli) d'une tâche"""
    task = await get_task_by_id_internal(task_id, db, task_service)
    if task is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    if not task.output or not task.output.result_path:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="No result file available for this task",
        )

    s3_key = task.output.result_path
    try:
        body = await s3_client_connector.aget_object(s3_key)
    except Exception:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Result file not found in storage",
        )

    # Build a meaningful filename from the original input filename
    base_name = task_id
    if task.input and task.input.raw_filename:
        base_name = task.input.raw_filename.rsplit(".", 1)[0]
    filename = f"{base_name}_rempli.odt"

    return StreamingResponse(
        io.BytesIO(body),
        media_type="application/vnd.oasis.opendocument.text",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/tasks/{task_id}/page/{page_number}")
async def get_task_page(
    task_id: str,
    page_number: int,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
) -> StreamingResponse:
    """Récupère une page spécifique d'une tâche"""
    task = await get_task_by_id_internal(task_id, db, task_service)
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")
    if not task.output or not task.output.pages:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="No result file available for this task",
        )
    s3_key = None
    if task.output and task.output.pages:
        for page in task.output.pages:
            if page.page == page_number - 1:
                if not page.page_url:
                    raise HTTPException(
                        status_code=http_status.HTTP_404_NOT_FOUND,
                        detail=f"Page {page_number} not found for this task",
                    )
                s3_key = normalize_page_url(page.page_url)
                break

    if s3_key is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Page {page_number} not found for this task",
        )
    try:
        body = await s3_client_connector.aget_object(s3_key)
    except Exception:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Result file not found in storage",
        )

    filename = f"{task_id}_page_{page_number}.png"

    return StreamingResponse(
        io.BytesIO(body),
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
        },
    )


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
    task_type: str,
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
    return await _rewrite_page_urls_async(updated_task)


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

    # Enrichir les tâches en file d'attente avec leur position
    for task in tasks:
        if task.status == TaskStatus.QUEUED.value:
            task.position = await task_service.get_position_in_queue(db, task.id, task.type)

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
    start_date: Optional[int] = Query(None, description="Timestamp début de période (epoch secondes)"),
    end_date: Optional[int] = Query(None, description="Timestamp fin de période (epoch secondes)"),
):
    """Récupère les statistiques des tâches, optionnellement filtrées par période"""
    skip = (page - 1) * page_size
    return await task_service.statistics(
        db,
        user_id=ctx.user_id or "",
        is_admin=bool(ctx.is_admin),
        skip=skip,
        limit=page_size,
        start_date=start_date,
        end_date=end_date,
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


@router.get(
    "/v1/leaderboard",
    response_model=LeaderboardResponse,
)
async def get_leaderboard(
    db: DbSessionDep,
    task_service: TaskServiceDep,
    ctx: TokenDep,
    task_type: Optional[str] = Query(None, description="Type de tâche (ex: ocr, forms, vectorize)"),
    start_date: Optional[int] = Query(None, description="Timestamp début de période (epoch secondes)"),
    end_date: Optional[int] = Query(None, description="Timestamp fin de période (epoch secondes)"),
):
    """Récupère le leaderboard : #1 + voisins autour de l'utilisateur courant"""
    if ctx.user_id is None:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    result = await task_service.get_leaderboard(
        db,
        user_id=ctx.user_id,
        task_type=task_type,
        start_date=start_date,
        end_date=end_date,
    )

    # Anonymiser les user_ids : "Vous" pour soi, "Utilisateur #rank" pour les autres
    for entry in result.entries:
        if entry.is_me:
            entry.user_id = "Vous"
        else:
            entry.user_id = f"Utilisateur #{entry.rank}"

    return result


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task_by_id(
    task_id: str,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
):
    """Supprime une tâche et ses sous-tâches"""
    task = await get_task_by_id_internal(task_id, db, task_service)
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Supprimer les tâches enfants d'abord
    children = await task_service.get_tasks_by_parent_id(db, task.id)
    for child in children:
        await task_service.delete_task_by_id(db, child.id, child.type)
        try:
            await s3_client_connector.adelete_by_task_id(user_id=child.user_id, task_id=child.id)
        except Exception as e:
            logger.error(f"Error occurred while deleting child task {child.id} from S3: {e}")

    await task_service.delete_task_by_id(db, task.id, task.type)

    try:
        await s3_client_connector.adelete_by_task_id(user_id=task.user_id, task_id=task.id)
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
            await s3_client_connector.adelete_by_task_id(user_id=task.user_id, task_id=task.id)
        except Exception as e:
            logger.error(f"Error occurred while deleting task from S3: {e}")


@router.get("/tasks/{task_id}/children", response_model=list[TaskModel])
async def get_task_children(
    task_id: str,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
):
    """Récupère les tâches enfants directes d'une tâche"""
    parent = await get_task_by_id_internal(task_id, db, task_service)
    if parent.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    children = await task_service.get_tasks_by_parent_id(db, task_id)
    return children


@router.get("/tasks/{task_id}/tree", response_model=list[TaskModel])
async def get_task_tree(
    task_id: str,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
):
    """Récupère une tâche et toutes ses sous-tâches"""
    parent = await get_task_by_id_internal(task_id, db, task_service)
    if parent.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    return await task_service.get_task_tree(db, task_id)


@router.post("/v1/tasks/submit", status_code=http_status.HTTP_201_CREATED)
async def submit_task(
    task_data: TaskForm,
    ctx: TokenDep,
    db: DbSessionDep,
    task_service: TaskServiceDep,
    task_name: CeleryTaskName = CeleryTaskName.OCR_TASK,
) -> TaskModel:
    """Crée une nouvelle tâche et la soumet immédiatement pour traitement"""
    if ctx.user_id is None:
        raise HTTPException(status_code=http_status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    new_task = await task_service.insert_new_task(
        db=db,
        user_id=ctx.user_id,
        form_data=task_data,
    )

    return new_task


@router.delete("/v1/tasks/revoke/{task_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_tasks_by_user_id(
    task_id: str,
    db: DbSessionDep,
    task_service: TaskServiceDep,
    ctx: TokenDep,
):
    """Révoque une tâche en cours d'exécution"""
    task = await get_task_by_id_internal(task_id, db, task_service)
    if task.user_id != ctx.user_id and not ctx.is_admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Task not found")

    celery_app.control.revoke(task_id, terminate=True)
    await task_service.update_task(
        db,
        task_id,
        task.type,
        form_data=TaskUpdateForm(status=TaskStatus.REVOKED.value),
    )
