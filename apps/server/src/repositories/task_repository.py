import time
import uuid
from datetime import datetime

from fastapi import HTTPException, status as http_status

from sqlalchemy import func, select

from sqlalchemy.ext.asyncio import AsyncSession
from src.logger import logger
from src.schemas.task import (
    TaskModel,
    TaskStatus,
    TaskUpdateForm,
    TaskForm,
    TaskStats,
    TaskStatsGlobal,
    TaskStatsUser,
)
from src.models.task import Task


class TaskRepository:
    async def insert_new_task(self, db: AsyncSession, user_id: str, form_data: TaskForm) -> TaskModel:
        _id = str(uuid.uuid4()) if not form_data.id else form_data.id

        result = Task(
            id=_id,
            type=form_data.type,
            status=TaskStatus.CREATED.value,
            percentage=0.0,
            user_id=user_id if not form_data.user_id else form_data.user_id,
            input=form_data.input.model_dump() if form_data.input else None,
            output=form_data.output.model_dump() if form_data.output else None,
            extras=form_data.extras,
            group_id=form_data.group_id,
            parameters=form_data.parameters,
            content_hash=form_data.content_hash,
            parent_id=form_data.parent_id,
            created_at=int(time.time()),
            updated_at=int(time.time()),
        )
        db.add(result)
        await db.commit()  # Flush pour générer l'ID avant de valider la transaction
        await db.refresh(result)
        return TaskModel.model_validate(result)

    async def get_task_by_id(self, db: AsyncSession, task_id: str, task_type: str) -> TaskModel:
        task = await db.get(Task, task_id)
        if not task:
            logger.warning(f"Task with id {task_id} not found.")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found.",
            )
        return TaskModel.model_validate(task)

    async def get_tasks_by_id(self, db: AsyncSession, task_id: str) -> list[TaskModel]:
        result = await db.execute(select(Task).filter(Task.id == task_id))
        tasks = result.scalars().all()
        if not tasks:
            logger.warning(f"Task with id {task_id} not found.")
            return []
        return [TaskModel.model_validate(task) for task in tasks]

    async def update_task(self, db: AsyncSession, task_id: str, task_type: str, form_data: TaskUpdateForm) -> TaskModel:

        task = await db.get(Task, task_id)
        if not task:
            logger.warning(f"Task with id {task_id} not found.")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found.",
            )

        updates = form_data.model_dump(exclude_unset=True)

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        if form_data.input:
            task.input = form_data.input.model_dump()

        if form_data.output:
            task.output = form_data.output.model_dump()

        task.updated_at = int(time.time())
        await db.commit()
        await db.refresh(task)
        return TaskModel.model_validate(task)

    async def delete_task_by_id(self, db: AsyncSession, task_id: str, task_type: str) -> TaskModel:
        task = await db.get(Task, task_id)
        if not task:
            logger.warning(f"Task with id {task_id} not found.")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found.",
            )
        await db.delete(task)
        await db.commit()
        return TaskModel.model_validate(task)

    async def get_tasks_by_user_id(
        self, db: AsyncSession, user_id: str, page: int = 1, page_size: int = 10
    ) -> list[TaskModel]:
        offset = (page - 1) * page_size

        result = await db.execute(
            select(Task)
            .filter(Task.user_id == user_id, Task.parent_id.is_(None))
            .order_by(Task.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        tasks = result.scalars().all()

        return [TaskModel.model_validate(task) for task in tasks]

    async def count_tasks_by_user_id(self, db: AsyncSession, user_id: str) -> int:
        result = await db.execute(select(func.count(Task.id)).filter(Task.user_id == user_id, Task.parent_id.is_(None)))
        count = result.scalar_one()
        return count

    async def delete_tasks_by_user_id(self, db: AsyncSession, user_id: str) -> list[TaskModel]:
        result = await db.execute(select(Task).filter(Task.user_id == user_id))
        tasks_to_delete = result.scalars().all()

        for task in tasks_to_delete:
            await db.delete(task)
        await db.commit()

        return [TaskModel.model_validate(task) for task in tasks_to_delete]

    async def get_position_in_queue(self, db: AsyncSession, task_id: str, task_type: str) -> int | None:

        task = await db.get(Task, task_id)
        if not task:
            return None

        if task.status != TaskStatus.QUEUED:
            return None

        result = await db.execute(
            select(func.count(Task.id)).filter(
                Task.status == TaskStatus.QUEUED,
                Task.created_at < task.created_at,
            )
        )
        position = result.scalar_one()

        return position

    async def get_task_by_content_hash(self, db: AsyncSession, content_hash_value: str) -> TaskModel:
        result = await db.execute(select(Task).filter(Task.content_hash == content_hash_value))
        task = result.scalars().first()
        if not task:
            logger.warning(f"Task with content hash {content_hash_value} not found.")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task with content hash {content_hash_value} not found.",
            )
        return TaskModel.model_validate(task)

    async def delete_tasks_by_date_and_status(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        status: TaskStatus,
    ) -> list[TaskModel]:
        result = await db.execute(
            select(Task).filter(
                Task.created_at >= int(start_date.timestamp()),
                Task.created_at <= int(end_date.timestamp()),
                Task.status == status.value,
            )
        )
        tasks_to_delete = result.scalars().all()
        results = [TaskModel.model_validate(task) for task in tasks_to_delete]
        for task in tasks_to_delete:
            await db.delete(task)
        await db.commit()

        return results

    async def get_tasks_by_group_id(
        self, db: AsyncSession, group_id: str, page: int = 1, page_size: int = 10
    ) -> list[TaskModel]:
        offset = (page - 1) * page_size
        result = await db.execute(select(Task).filter(Task.group_id == group_id).offset(offset).limit(page_size))
        tasks = result.scalars().all()

        return [TaskModel.model_validate(task) for task in tasks]

    async def delete_tasks_by_group_id(self, db: AsyncSession, group_id: str) -> list[TaskModel]:
        result = await db.execute(select(Task).filter(Task.group_id == group_id))
        tasks_to_delete = result.scalars().all()

        for task in tasks_to_delete:
            await db.delete(task)
        await db.commit()

        return [TaskModel.model_validate(task) for task in tasks_to_delete]

    async def statistics(
        self,
        db: AsyncSession,
        user_id: str,
        is_admin: bool = False,
        skip: int = 0,
        limit: int = 10,
    ) -> TaskStats:
        """Récupère les statistiques globales et par utilisateur"""
        # Statistiques globales
        total_tasks_result = await db.execute(select(func.count(Task.id)))
        total_tasks = total_tasks_result.scalar_one()

        tasks_stats_result = await db.execute(select(Task.status, func.count(Task.id)).group_by(Task.status))
        tasks_stats = tasks_stats_result.all()
        tasks_stats_dict = {status: count for status, count in tasks_stats}

        global_stats = TaskStatsGlobal(total_tasks=total_tasks, tasks_stats=tasks_stats_dict)

        # Statistiques de l'utilisateur courant
        user_total_tasks_result = await db.execute(select(func.count(Task.id)).filter(Task.user_id == user_id))
        user_total_tasks = user_total_tasks_result.scalar_one()

        user_tasks_stats_result = await db.execute(
            select(Task.status, func.count(Task.id)).filter(Task.user_id == user_id).group_by(Task.status)
        )
        user_tasks_stats = user_tasks_stats_result.all()
        user_tasks_stats_dict = {status: count for status, count in user_tasks_stats}
        user_stats = TaskStatsUser(
            user_id=user_id,
            total_tasks=user_total_tasks,
            tasks_stats=user_tasks_stats_dict,
        )

        return TaskStats(global_stats=global_stats, user_stats=user_stats)

    async def count_unique_users_between_dates(self, db: AsyncSession, start_date: int, end_date: int) -> int:
        """Compte le nombre d'utilisateurs uniques entre deux dates"""
        result = await db.execute(
            select(func.count(func.distinct(Task.user_id))).filter(
                Task.created_at >= start_date, Task.created_at <= end_date
            )
        )
        unique_users = result.scalar_one()
        return unique_users

    async def fetch_tasks_by_parent_id(self, db: AsyncSession, parent_id: str) -> list[TaskModel]:
        """Récupère les tâches enfants d'une tâche par son ID parent"""
        result = await db.execute(select(Task).filter(Task.parent_id == parent_id))
        child_tasks = result.scalars().all()
        return [TaskModel.model_validate(task) for task in child_tasks]

    async def get_task_tree(self, db: AsyncSession, task_id: str) -> list[TaskModel]:
        """Récupère une tâche et toutes ses tâches enfants récursivement"""
        result = await db.execute(select(Task).filter(Task.id == task_id))
        root_task = result.scalars().first()
        if not root_task:
            logger.warning(f"Task with id {task_id} not found.")
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task with id {task_id} not found.",
            )

        tasks_tree = []

        tasks_tree.append(TaskModel.model_validate(root_task))
        child_tasks = await self.fetch_tasks_by_parent_id(db, task_id)
        tasks_tree.extend(child_tasks)

        return tasks_tree
