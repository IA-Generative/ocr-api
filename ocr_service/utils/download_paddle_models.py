from paddleocr import PaddleOCR

# Initialize PaddleOCR instance
PaddleOCR(
    use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False, ocr_version="PP-OCRv5"
)
