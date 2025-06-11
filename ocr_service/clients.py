from ocr_service.configs.paddle import PaddleSetting
from ocr_service.models.paddle_ocr import PaddleInferOCR
from ocr_service.workers.ocr_worker import OCRWorker
from src.config.ocr_model import OCRModelSettings
from src.connector.base import BaseFileConnector

model_settings = OCRModelSettings()


def get_ocr_processor(file_connector: BaseFileConnector) -> OCRWorker:
    ocr_settings = PaddleSetting()
    ocr_model = PaddleInferOCR(
        device=ocr_settings.DEVICE,
        batch_size=ocr_settings.DETECTION_BATCH_SIZE,
        ocr_version=ocr_settings.OCR_VERSION,
    )

    return OCRWorker(file_connector=file_connector, ocr_model=ocr_model, settings=ocr_settings)
