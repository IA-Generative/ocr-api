import boto3

from services.base.worker import BaseWorker
from src.connector import S3Connector, s3_settings

s3_client = boto3.client("s3")
s3_client_connector = S3Connector(s3_client=s3_client, bucket_name=s3_settings.S3_BUCKET_NAME)
worker_name = "worker.task.ocr"


def load_worker(name: str, batch_size: int = 1, worker_weight: float = 1) -> BaseWorker:
    model = None
    if name == "ocr":
        from ocr_service.workers.ocr_worker import OCRResult

        model = OCRResult(type="ocr", model_name="")

    elif name == "checkbox":
        from business.checkbox_service.models.box_detection import BoxDetection

        model = BoxDetection()
    else:
        raise NotImplementedError("")

    return BaseWorker(
        name=name,
        file_connector=s3_client_connector,
        model=model,
        batch_size=batch_size,
        worker_weight=worker_weight,
    )
