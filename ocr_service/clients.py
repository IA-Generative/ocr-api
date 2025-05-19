import os
from ocr_service.configs.paddle import PaddleSetting
from ocr_service.models.docling_ocr import DoclingInferOCR
from ocr_service.workers.ocr_worker import OCRWorker
from src.config.ocr_model import OCRModelSettings
from src.connector.base import BaseFileConnector

model_settings = OCRModelSettings()


def get_ocr_processor(file_connector: BaseFileConnector) -> OCRWorker:
    ocr_settings = PaddleSetting()
    
    if os.environ.get("MODEL_NAME") == "docling":
        ocr_model = DoclingInferOCR()
    else:
        from ocr_service.models.paddle_ocr import PaddleInferOCR

        ocr_model = PaddleInferOCR(path_model=ocr_settings.PADDLE_OCR_BASE_DIR)

    return OCRWorker(
        file_connector=file_connector, ocr_model=ocr_model, settings=ocr_settings
    )
