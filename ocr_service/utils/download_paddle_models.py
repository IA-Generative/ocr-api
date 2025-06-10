import os
from paddleocr import PaddleOCR

ocr_version = os.environ.get("PADDLE_OCR_VERSION", "PP-OCRv3")

PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    ocr_version=ocr_version,
)
