from ocr_service.configs.paddle import PaddleSetting
from ocr_service.models.paddle_ocr import PaddleInferOCR

ocr_settings = PaddleSetting()
ocr_model = PaddleInferOCR(
    device=ocr_settings.DEVICE,
    batch_size=ocr_settings.DETECTION_BATCH_SIZE,
    ocr_version=ocr_settings.OCR_VERSION,
    lang=ocr_settings.OCR_LANG,
)
