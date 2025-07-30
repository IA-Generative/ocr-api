from services.base.worker import BaseWorker
from src.schemas.task import TaskModel
from src.logger import logger


class Pipeline:
    def __init__(self, workers: list[BaseWorker]):
        self.workers = workers

    def process(self, task: TaskModel) -> TaskModel:
        for worker in self.workers:
            logger.info(f"Processing task {task.id} with worker {worker.name}")
            if worker.is_applicable(task):
                logger.info(f"Worker {worker.name} is applicable for task {task.id}")
                return worker.process_task(task)
        return task
