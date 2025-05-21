from datetime import datetime
import uuid
import time
from typing import Dict, Optional, Any
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, String, JSON, FLOAT, BigInteger, Integer

#from src.connector import get_db, Base
from src.connector.db_connector import get_db, Base
from src.logger import logger


class TaskStats(Base):
    __tablename__ = "tasks_stats"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    status = Column(String, default="queued")
    percentage = Column(FLOAT, nullable=False)
    nb_total_item = Column(Integer, nullable=True)
    model_name = Column(String, nullable=True)
    version = Column(String, nullable=True)
    up_vote = Column(Integer, nullable=False, default=0)
    down_vote = Column(Integer, nullable=False, default=0)

    created_at = Column(BigInteger, default=lambda: int(datetime.now().timestamp()))

    updated_at = Column(
        BigInteger,
        default=lambda: int(datetime.now().timestamp()),
        onupdate=lambda: int(datetime.now().timestamp()),
    )

    extras = Column(JSON, nullable=True)


class TaskStatsModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    type: str
    status: str = "queued"
    percentage: Optional[float] = 0.0
    nb_total_item: Optional[int] = None
    model_name: Optional[str] = None
    version: Optional[str]
    up_vote: int = 0
    down_vote: int = 0

    created_at: int
    updated_at: int
    extras: Optional[Dict[str, Any]] = None


class TaskStatsForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: Optional[str] = None
    status: str
    percentage: Optional[float] = 0.0
    nb_total_item: Optional[int] = None
    model_name: Optional[str] = None
    version: Optional[str] = None
    extras: Optional[dict] = None


class TaskStatsUpdateForm(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    type: Optional[str] = None
    status: Optional[str] = None
    percentage: Optional[float] = 0.0
    extras: Optional[dict] = None
    nb_total_item: Optional[int] = None
    model_name: Optional[str] = None
    version: Optional[str] = None
    extras: Optional[dict] = None


class TaskStatTable:
    def insert_new_task(self, form_data: TaskStatsForm) -> Optional[TaskStatsModel]:
        with get_db() as db:
            knowledge = TaskStatsModel(
                **{
                    **form_data.model_dump(),
                    "id": str(uuid.uuid4()),
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )

            result = TaskStats(**knowledge.model_dump())
            db.add(result)
            db.commit()
            db.refresh(result)
            return TaskStatsModel.model_validate(result)

    def get_task_by_id(self, task_id: str) -> Optional[TaskStatsModel]:
        with get_db() as db:
            task = db.query(TaskStats).filter(TaskStats.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found.")
                return None
            return TaskStatsModel.model_validate(task)

    def up_vote(self, task_id: str) -> Optional[TaskStatsModel]:
        with get_db() as db:
            task = db.query(TaskStats).filter(TaskStats.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found.")
                return None

            task.up_vote += 1
            db.commit()
            db.refresh(task)
            return TaskStatsModel.model_validate(task)

    def down_vote(self, task_id: str) -> Optional[TaskStatsModel]:
        with get_db() as db:
            task = db.query(TaskStats).filter(TaskStats.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found.")
                return None

            task.down_vote += 1
            db.commit()
            db.refresh(task)
            return TaskStatsModel.model_validate(task)

    def update_task(
        self, task_id: str, form_data: TaskStatsForm
    ) -> Optional[TaskStatsModel]:
        with get_db() as db:
            task = db.query(TaskStats).filter(TaskStats.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found.")
                return None

            updates = form_data.model_dump(exclude_unset=True)

            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)

            db.commit()
            db.refresh(task)
            return TaskStatsModel.model_validate(task)

    def delete_task_by_id(self, task_id: str) -> Optional[TaskStatsModel]:
        with get_db() as db:
            task = db.query(TaskStats).filter(TaskStats.id == task_id).first()
            if not task:
                logger.warning(f"Task with id {task_id} not found.")
                return None
            db.delete(task)
            db.commit()
            return TaskStatsModel.model_validate(task)


task_stat_table = TaskStatTable()
