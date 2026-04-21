from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.task import (
    TaskModel,
    TaskStatus,
    TaskUpdateForm,
    TaskForm,
    TaskStats,
)
from src.repositories.task_repository import TaskRepository


class TaskService:
    """Service pour gérer les tâches via le repository async"""

    def __init__(self):
        self.task_repo = TaskRepository()

    async def insert_new_task(self, db: AsyncSession, user_id: str, form_data: TaskForm) -> TaskModel:
        """Crée une nouvelle tâche"""
        task = await self.task_repo.insert_new_task(db, user_id, form_data)
        return task

    async def get_task_by_id(self, db: AsyncSession, task_id: str, task_type: str) -> TaskModel:
        """Récupère une tâche par son ID et type"""
        return await self.task_repo.get_task_by_id(db, task_id, task_type)

    async def get_tasks_by_id(self, db: AsyncSession, task_id: str) -> list[TaskModel]:
        """Récupère toutes les tâches avec un ID donné (peut avoir plusieurs types)"""
        return await self.task_repo.get_tasks_by_id(db, task_id)

    async def update_task(self, db: AsyncSession, task_id: str, task_type: str, form_data: TaskUpdateForm) -> TaskModel:
        """Met à jour une tâche"""
        return await self.task_repo.update_task(db, task_id, task_type, form_data)

    async def delete_task_by_id(self, db: AsyncSession, task_id: str, task_type: str) -> TaskModel:
        """Supprime une tâche par son ID et type"""
        return await self.task_repo.delete_task_by_id(db, task_id, task_type)

    async def get_tasks_by_user_id(
        self, db: AsyncSession, user_id: str, page: int = 1, page_size: int = 10
    ) -> list[TaskModel]:
        """Récupère les tâches d'un utilisateur avec pagination"""
        return await self.task_repo.get_tasks_by_user_id(db, user_id, page, page_size)

    async def count_tasks_by_user_id(self, db: AsyncSession, user_id: str) -> int:
        """Compte le nombre de tâches d'un utilisateur"""
        return await self.task_repo.count_tasks_by_user_id(db, user_id)

    async def delete_tasks_by_user_id(self, db: AsyncSession, user_id: str) -> list[TaskModel]:
        """Supprime toutes les tâches d'un utilisateur"""
        return await self.task_repo.delete_tasks_by_user_id(db, user_id)

    async def get_position_in_queue(self, db: AsyncSession, task_id: str, task_type: str) -> int | None:
        """Récupère la position d'une tâche dans la file d'attente"""
        return await self.task_repo.get_position_in_queue(db, task_id, task_type)

    async def get_task_by_content_hash(self, db: AsyncSession, content_hash_value: str) -> TaskModel:
        """Récupère une tâche par son hash de contenu"""
        return await self.task_repo.get_task_by_content_hash(db, content_hash_value)

    async def delete_tasks_by_date_and_status(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime,
        status: TaskStatus,
    ) -> list[TaskModel]:
        """Supprime les tâches avec un statut donné dans une plage de dates"""
        return await self.task_repo.delete_tasks_by_date_and_status(db, start_date, end_date, status)

    async def get_tasks_by_group_id(
        self, db: AsyncSession, group_id: str, page: int = 1, page_size: int = 10
    ) -> list[TaskModel]:
        """Récupère les tâches d'un groupe avec pagination"""
        return await self.task_repo.get_tasks_by_group_id(db, group_id, page, page_size)

    async def delete_tasks_by_group_id(self, db: AsyncSession, group_id: str) -> list[TaskModel]:
        """Supprime toutes les tâches d'un groupe"""
        return await self.task_repo.delete_tasks_by_group_id(db, group_id)

    async def statistics(
        self,
        db: AsyncSession,
        user_id: str,
        is_admin: bool = False,
        skip: int = 0,
        limit: int = 10,
        start_date: int | None = None,
        end_date: int | None = None,
    ) -> TaskStats:
        """Récupère les statistiques globales et par utilisateur"""
        return await self.task_repo.statistics(db, user_id, is_admin, skip, limit, start_date, end_date)

    async def count_unique_users_between_dates(self, db: AsyncSession, start_date: int, end_date: int) -> int:
        """Compte le nombre d'utilisateurs uniques entre deux dates"""
        return await self.task_repo.count_unique_users_between_dates(db, start_date, end_date)

    async def get_tasks_by_parent_id(self, db: AsyncSession, parent_id: str) -> list[TaskModel]:
        """Récupère les tâches enfants directes d'une tâche"""
        return await self.task_repo.fetch_tasks_by_parent_id(db, parent_id)

    async def get_task_tree(self, db: AsyncSession, task_id: str) -> list[TaskModel]:
        """Récupère une tâche et toutes ses tâches enfants"""
        return await self.task_repo.get_task_tree(db, task_id)
