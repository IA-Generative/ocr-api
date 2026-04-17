import json

from src.logger import logger
from src.schemas.task import TaskModel


def validate_task(task_info: dict | str) -> TaskModel:
    try:
        task_info = task_info if isinstance(task_info, dict) else json.loads(task_info)
        task = TaskModel.model_validate(task_info)
        return task
    except Exception as e:
        logger.error(f"Error validating task: {e}")
        raise ValueError(f"Invalid task data: {e}")
