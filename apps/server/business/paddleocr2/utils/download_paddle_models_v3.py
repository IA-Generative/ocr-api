import logging
from paddleocr import PaddleOCR

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


if __name__ == "__main__":
    PaddleOCR(
        lang="fr",
        ocr_version="PP-OCRv3",
    )
