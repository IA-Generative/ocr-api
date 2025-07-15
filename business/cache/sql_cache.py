from services.base.cache import BaseCache
from src.schemas.task import TaskModel, task_table, TaskStatus


class TaskCache(BaseCache):
    def is_in_cache(self, task: TaskModel) -> bool:
        found_task = task_table.get_task_by_content_hash(content_hash_value=task.content_hash)
        return found_task is not None and found_task.status == TaskStatus.COMPLETED.value

    def get_task_from_cache(self, task: TaskModel) -> TaskModel:
        return task_table.get_task_by_content_hash(content_hash_value=task.content_hash)
