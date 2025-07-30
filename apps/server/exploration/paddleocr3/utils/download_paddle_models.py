from business.paddleocr3.config import PaddleSetting
from business.paddleocr3.models.paddle_pipe import PaddleInferOCR
from business.paddleocr3.models.formula import PaddleFormulaRecognizer
from business.paddleocr3.models.layout import PaddleLayoutDetection
from business.paddleocr3.models.table import TablePrediction

ocr_settings = PaddleSetting()
PaddleInferOCR(
    batch_size=ocr_settings.DETECTION_BATCH_SIZE,
    ocr_version=ocr_settings.OCR_VERSION,
    lang=ocr_settings.OCR_LANG,
    text_detection_model_name=f"{ocr_settings.OCR_VERSION}_mobile_det",
    text_recognition_model_name=f"{ocr_settings.OCR_VERSION}_mobile_rec",
)
PaddleLayoutDetection()
PaddleFormulaRecognizer()
TablePrediction()
