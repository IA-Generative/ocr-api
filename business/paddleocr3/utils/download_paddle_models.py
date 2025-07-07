from business.paddleocr3.config import PaddleSetting
from business.paddleocr3.models.paddle import PaddleInferOCR
from business.paddleocr3.models.formula import PaddleFormulaRecognizer
from business.paddleocr3.models.layout import PaddleLayoutDetection

ocr_settings = PaddleSetting()
PaddleInferOCR(
    batch_size=ocr_settings.DETECTION_BATCH_SIZE,
    ocr_version=ocr_settings.OCR_VERSION,
    lang=ocr_settings.OCR_LANG,
)
PaddleLayoutDetection()
PaddleFormulaRecognizer()
