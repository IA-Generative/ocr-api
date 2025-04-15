from pydantic_settings import BaseSettings


class SuryaSetting(BaseSettings):
    SURYA_DETECTION_FOLDER: str = "./models/text_detection/2025_02_28"
    SURYA_RECOGNITION_FOLDER: str = "./models/text_recognition/2025_02_18"
    SURYA_S3_DETECTION_PATH: str = "text_detection/2025_02_18"
    SURYA_S3_RECOGNITION_PATH: str = "text_recognition/2025_02_18"
