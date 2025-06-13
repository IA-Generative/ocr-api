import boto3

from services.base.worker import BaseWorker
from src.connector import S3Connector, s3_settings

s3_client = boto3.client("s3")
s3_client_connector = S3Connector(s3_client=s3_client, bucket_name=s3_settings.S3_BUCKET_NAME)


def load_worker(name: str, batch_size: int = 1, worker_weight: float = 1) -> BaseWorker:
    model = None
    if name == "paddleocr-2.10.0":
        from business.paddleocr2.models.paddle import PaddleInferOCR2
        from business.paddleocr2.configs.paddle import PaddleSetting

        model = PaddleInferOCR2(PaddleSetting().PADDLE_OCR_BASE_DIR)

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
