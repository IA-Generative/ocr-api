from .task import Task
from .task_stats import TaskStatTable
from src.connector import Base, engine

__all__ = ["Task", "TaskStatTable"]

Base.metadata.create_all(engine)
