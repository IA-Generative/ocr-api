from services.base.worker import BaseWorker
from src.schemas.task import TaskModel
from business.chunks.models.chunk_saver import OcrChunkSaver
from business.chunks.models.chunker import OcrChunker
from src.logger import logger


class ChunkWorker(BaseWorker):
    def __init__(self, name: str, batch_size: int = 1, worker_weight: float = 0):
        super().__init__(
            name=name,
            models=[],
            batch_size=batch_size,
            worker_weight=worker_weight,
            file_connector=None,
            cache=None,
        )
        self.ocr_chunker = OcrChunker()  # You can specify models if needed
        self.ocr_chunk_saver = OcrChunkSaver()

    def is_applicable(self, task: TaskModel) -> bool:
        if task.output and task.output.pages and len(task.output.pages) > 0 and task.content_hash:
            return True
        return False

    def _process_task(self, task: TaskModel) -> TaskModel:
        condition = task.output and task.output.pages and len(task.output.pages) > 0 and task.content_hash
        logger.info(f"Checking if task {task.id} is applicable for chunking: {condition}")
        if not condition:
            logger.warning(f"Task {task.id} is not applicable for chunking. Skipping.")
            return task
        logger.info(f"Processing task {task.id} with {len(task.output.pages)} pages for chunking.")
        chunks = self.ocr_chunker.chunk_pages(
            content_hash=task.content_hash,
            pages=task.output.pages,  # type: ignore
        )
        self.ocr_chunk_saver.save(chunks=chunks)

        return task
