from pydantic_settings import BaseSettings, SettingsConfigDict


class PaddleSetting(BaseSettings):
    PADDLE_OCR_BASE_DIR: str = "models/"
    PADDLE_PDX_CACHE_HOME: str = "models/paddle_pdx_cache/"
    DETECTION_FOLDER: str = "detection"
    RECOGNITION_FOLDER: str = "recognition"
    CLASSIFICATION_FOLDER: str = "classification"
    DETECTION_BATCH_SIZE: int = 2
    RECOGNITION_BATCH_SIZE: int = 8
    CPU_THREADS: int = 2
    ENABLE_MKLDNN: bool = True
    OCR_VERSION: str = "PP-OCRv3"
    LAYOUT_MODEL_NAME: str = "PP-DocLayoutV2"
    DEVICE: str = "cpu"
    CLIP_MODEL_DIR: str = "/app/models/clip"
    OCR_LANG: str | None = None
    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")
