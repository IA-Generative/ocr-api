from services.base.worker import BaseWorker
from src.schemas.task import TaskModel


class ClassificationWorker(BaseWorker):
    def __init__(
        self,
        name: str,
        file_connector,
        models: list,
        batch_size: int = 1,
        worker_weight: float = 1,
        cache=None,
    ):
        super().__init__(
            name=name,
            file_connector=file_connector,
            models=models,
            batch_size=batch_size,
            worker_weight=worker_weight,
            cache=cache,
        )

    def is_applicable(self, task: TaskModel) -> bool:
        return True
