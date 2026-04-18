from src.connector.broker_connector import celery_app
from src.logger import logger

import services.tasks.classification  # noqa: F401 - registers PAGE_TEXT_CLASSIFICATION_TASK
import services.tasks.ocr_tasks  # noqa: F401 - registers OCR_TASK
import services.tasks.image_classification  # noqa: F401 - registers PAGE_CLASSIFICATION_TASK
import services.tasks.ocr_chunk_task  # noqa: F401 - registers OCR_CHUNK_TASK
import services.tasks.signal  # noqa: F401 - registers task signals
import services.tasks.entity_extractions_task  # noqa: F401 - registers ENTITY_EXTRACTION_TASK


if __name__ == "__main__":
    logger.info("Start to consume...")
    celery_app.start()
