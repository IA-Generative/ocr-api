from datetime import datetime
import uuid
import time
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, DateTime, JSON, FLOAT, BigInteger

from src.internal.db import get_db, Base
from src.logger import logger


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    status = Column(String, default="queued")
    user_id = Column(String, nullable=False)
    percentage = Column(FLOAT, nullable=False)

    created_at = Column(
        BigInteger, default=lambda: int(datetime.now().timestamp()))
    updated_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()),
                        onupdate=lambda: int(datetime.now().timestamp()))

    extras = Column(JSON, nullable=True)


class TaskModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    type: str
    status: str = "queued"
    percentage: Optional[float] = 0.0

    created_at: int
    updated_at: int
    extras: Optional[Dict[str, Any]] = None


class TaskForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    type: Optional[str] = None
    status: str
    percentage: Optional[float] = 0.0
    extras: Optional[dict] = None


class TaskUpdateForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: Optional[str] = None
    status: Optional[str] = None
    percentage: Optional[float] = 0.0
    extras: Optional[dict] = None


class TaskTable:

    def insert_new_task(
        self, user_id: str, form_data: TaskForm
    ) -> Optional[TaskModel]:
        with get_db() as db:
            knowledge = TaskModel(
                **{
                    **form_data.model_dump(),
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time())
                }
            )

            try:
                result = Task(**knowledge.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)
                if result:
                    return TaskModel.model_validate(result)
                else:
                    return None
            except Exception as e:
                logger.error(f"{e}")
                return None

    def get_task_by_id(self, task_id: str) -> Optional[TaskModel]:
        with get_db() as db:
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    logger.warning(f"Task with id {task_id} not found.")
                    return None
                return TaskModel.model_validate(task)
            except Exception as e:
                logger.error(f"Failed to get task {task_id}: {e}")

    def update_task(
        self, task_id: str, form_data: TaskUpdateForm
    ) -> Optional[TaskModel]:
        with get_db() as db:
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    logger.warning(f"Task with id {task_id} not found.")
                    return None

                updates = form_data.model_dump(exclude_unset=True)

                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)

                task.updated_at = int(time.time())
                db.commit()
                db.refresh(task)
                return TaskModel.model_validate(task)

            except Exception as e:
                logger.error(f"Failed to update task {task_id}: {e}")
                return None

    def delete_task_by_id(self, task_id: str) -> Optional[TaskModel]:

        with get_db() as db:
            try:
                task = db.query(Task).filter(Task.id == task_id).first()
                if not task:
                    logger.warning(f"Task with id {task_id} not found.")
                    return None
                db.delete(task)
                db.commit()
                return TaskModel.model_validate(task)
            except Exception as e:
                logger.error(e)

    def get_tasks_by_user_id(self, user_id: str, page: int = 1, page_size: int = 10) -> Optional[List[TaskModel]]:
        offset = (page - 1) * page_size
        try:
            with get_db() as db:
                tasks = db.query(Task).filter(Task.user_id == user_id).offset(
                    offset).limit(page_size).all()

                if not tasks:
                    logger.warning(f"No tasks found for user {user_id}.")
                    return None

                return [TaskModel.model_validate(task) for task in tasks]
        except Exception as e:
            logger.error(f"Failed to get tasks for user {user_id}: {e}")
            return None

    def delete_tasks_by_user_id(self, user_id: str) -> Optional[List[TaskModel]]:
        try:
            with get_db() as db:
                tasks_to_delete = db.query(Task).filter(
                    Task.user_id == user_id).all()

                if not tasks_to_delete:
                    logger.warning(f"No tasks found for user {user_id}.")
                    return None

                for task in tasks_to_delete:
                    db.delete(task)
                db.commit()

                return [TaskModel.model_validate(task) for task in tasks_to_delete]

        except Exception as e:
            logger.error(f"Failed to delete tasks for user {user_id}: {e}")
            return None


task_table = TaskTable()
