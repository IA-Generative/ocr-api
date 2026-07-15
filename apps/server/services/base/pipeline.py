from typing import Protocol, runtime_checkable

from src.schemas.task import TaskModel
from src.logger import logger, Colors


@runtime_checkable
class ProcessWorker(Protocol):
    """Contrat minimal requis par ``Pipeline`` : un worker OCR (``BaseWorker``)
    ou tout autre worker (ex: ``YoutubeTranscriptionWorker``) qui l'implémente."""

    name: str

    def is_applicable(self, task: TaskModel) -> bool: ...

    def process_task(self, task: TaskModel) -> TaskModel: ...


class Pipeline:
    def __init__(self, workers: list[ProcessWorker]):
        self.workers = workers

    def process(self, task: TaskModel) -> TaskModel:
        for worker in self.workers:
            logger.info(f"{Colors.CYAN}Processing task {task.id} with worker {worker.name}{Colors.RESET}")
            if worker.is_applicable(task):
                logger.info(f"{Colors.GREEN}Worker {worker.name} is applicable for task {task.id}{Colors.RESET}")
                return worker.process_task(task)
        return task
