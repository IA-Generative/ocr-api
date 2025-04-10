from src.logger import logger
from src.connector.base import BaseFileConnector
from src.config.connector import ConnectorSettings

from ocr_service.workers.ocr_worker import OCRWorker
from src.config.ocr_model import OCRModelSettings


AVAILABLE_MODEL = ["paddle", "surya"]
connector_settings = ConnectorSettings()
model_settings = OCRModelSettings()


def get_file_connector(
    connector_settings: ConnectorSettings = connector_settings,
) -> BaseFileConnector:
    if connector_settings.S3_AVAILABLE == connector_settings.MINIO_AVAILABLE:
        msg = (
            f"Minio and S3 settings ar both set has ({connector_settings.S3_AVAILABLE})"
        )
        logger.error(msg)
        raise Exception(msg)

    if connector_settings.S3_AVAILABLE == "True":
        from src.config.s3 import S3Settings
        from src.connector.s3_connector import S3Connector
        import boto3

        settings = S3Settings()
        s3_client = boto3.client(
            "s3",
            use_ssl=True,
            endpoint_url=settings.S3_END_POINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
        )
        return S3Connector(s3_client=s3_client, bucket_name=settings.S3_BUCKET_NAME)
    if connector_settings.MINIO_AVAILABLE == "True":
        import minio
        from src.config.minio import MinioSettings
        from src.connector.minio_connector import MinioConnector

        minio_settings = MinioSettings()
        minio_client = minio.Minio(
            endpoint=minio_settings.MINIO_END_POINT,
            access_key=minio_settings.MINIO_ACCESS_KEY,
            secret_key=minio_settings.MINIO_SECRET_KEY,
            secure=False,
        )
        return MinioConnector(
            minio_client=minio_client, bucket_name=minio_settings.MINIO_BUCKET_NAME
        )


def get_ocr_processor(
    model_settings: OCRModelSettings = model_settings,
    connector_settings: ConnectorSettings = connector_settings,
) -> OCRWorker:
    file_connector = get_file_connector(connector_settings=connector_settings)
    model_name = model_settings.MODEL_NAME
    if model_name == "surya":
        from ocr_service.configs.surya import SuryaSetting
        from ocr_service.models.surya_ocr import SuryaOCR

        ocr_settings = SuryaSetting()
        ocr_model = SuryaOCR(
            checkpoint_detection=ocr_settings.SURYA_DETECTION_FOLDER,
            checkpoint_recognition=ocr_settings.SURYA_RECOGNITION_FOLDER,
        )

    elif model_name == "paddle":
        from ocr_service.configs.paddle import PaddleSetting
        from ocr_service.models.paddle_ocr import PaddleInferOCR

        ocr_settings = PaddleSetting()
        ocr_model = PaddleInferOCR(path_model=ocr_settings.PADDLE_OCR_BASE_DIR)

    else:
        raise NotImplementedError(
            f"{model_name} is not available yet ({AVAILABLE_MODEL})"
        )
    return OCRWorker(
        minio_connector=file_connector, ocr_model=ocr_model, settings=ocr_settings
    )
