import os
import boto3

from services.base.worker import BaseWorker
from business.checkbox_service.models.box_detection import BoxDetection

from src.connector import S3Connector, s3_settings
from src.logger import logger

s3_client = boto3.client("s3")
s3_client_connector = S3Connector(s3_client=s3_client, bucket_name=s3_settings.S3_BUCKET_NAME)

DEVICE = os.environ.get("DEVICE", "cpu")

def load_worker(name: str, batch_size: int = 1, worker_weight: float = 1) -> BaseWorker:
    logger.info(f"---- {name} selected ----")
    models = []
    model = None
    if name == "paddleocr-2.10.0":
        from business.paddleocr2.models.paddle import PaddleInferOCR2
        from business.paddleocr2.configs.paddle import PaddleSetting

        model = PaddleInferOCR2(PaddleSetting().PADDLE_OCR_BASE_DIR)

    elif name == "paddleocr-3.0.1":
        from business.paddleocr3.models.paddle import PaddleInferOCR

        model = PaddleInferOCR()

    elif name == "paddleocr-3.0.1-pipeline":
        from business.paddleocr3.models.paddle import PaddleInferOCR
        from business.paddleocr3.models.layout import PaddleLayoutDetection
        from business.paddleocr3.models.formula import PaddleFormulaPredcition
        from business.paddleocr3.models.pipeline import PipelineLinearPrediction

        model = PipelineLinearPrediction(
            models=[
                PaddleInferOCR(device=DEVICE),
                PaddleLayoutDetection(device=DEVICE),
                PaddleFormulaPredcition(device=DEVICE),
            ]
        )

    else:
        raise NotImplementedError("")

    models.append(model)
    models.append(BoxDetection())

    return BaseWorker(
        name=name,
        file_connector=s3_client_connector,
        models=models,
        batch_size=batch_size,
        worker_weight=worker_weight,
    )
