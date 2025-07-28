from pydantic_settings import BaseSettings


class PaddleSetting(BaseSettings):
    PADDLE_OCR_BASE_DIR: str = "models/"
    DETECTION_FOLDER: str = "detection"
    RECOGNITION_FOLDER: str = "recognition"
    CLASSIFICATION_FOLDER: str = "classification"
    DETECTION_BATCH_SIZE: int = 2
    RECOGNITION_BATCH_SIZE: int = 4
    OCR_VERSION: str = "PP-OCRv4"
    DEVICE: str = "cpu"
    OCR_LANG: str | None = "en"
    USE_LAYOUT_DETECTION: bool = True
    USE_FORMULA_RECOGNITION: bool = True
    USE_TABLE_RECOGNITION: bool = False
