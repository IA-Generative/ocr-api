from .task import Task
from .task_stats import TaskStatTable
from src.internal.db import Base, engine

__all__ = ["Task", "TaskStatTable"]

Base.metadata.create_all(engine)
