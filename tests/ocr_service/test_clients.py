import pytest
from ocr_service.clients import get_file_connector, get_ocr_processor
from src.config.connector import ConnectorSettings
from src.config.ocr_model import OCRModelSettings
from src.connector.minio_connector import MinioConnector
from ocr_service.models.paddle_ocr import PaddleInferOCR
from ocr_service.models.surya_ocr import SuryaOCR

s3_available = ConnectorSettings().S3_AVAILABLE == "True"


def test_get_file_connector_error():
    connector_settings = ConnectorSettings()
    with pytest.raises(Exception):
        connector_settings.MINIO_AVAILABLE = "True"
        connector_settings.S3_AVAILABLE = "True"
        get_file_connector(connector_settings)

    with pytest.raises(Exception):
        connector_settings.MINIO_AVAILABLE = "False"
        connector_settings.S3_AVAILABLE = "False"
        get_file_connector(connector_settings)


def test_get_file_connector_minio():
    connector_settings = ConnectorSettings()

    connector_settings.MINIO_AVAILABLE = "True"
    connector_settings.S3_AVAILABLE = "False"
    file_connector = get_file_connector(connector_settings)
    assert isinstance(file_connector, MinioConnector)


@pytest.mark.skipif(not s3_available, reason="S3 is not available for testing")
def test_get_file_connector_s3():
    connector_settings = ConnectorSettings()

    connector_settings.MINIO_AVAILABLE = "False"
    connector_settings.S3_AVAILABLE = "True"
    file_connector = get_file_connector(connector_settings)
    assert isinstance(file_connector, MinioConnector)


def test_get_process_ocr_raise_model_not_found():
    model_settings = OCRModelSettings()
    model_settings.MODEL_NAME = "Mis"
    with pytest.raises(NotImplementedError):
        get_ocr_processor(model_settings=model_settings)


def test_get_process_ocr_paddle():
    model_settings = OCRModelSettings()
    actual = get_ocr_processor(model_settings=model_settings)
    assert isinstance(actual.ocr_model, PaddleInferOCR)


def test_get_process_ocr_surya():
    model_settings = OCRModelSettings()
    model_settings.MODEL_NAME = "surya"
    actual = get_ocr_processor(model_settings=model_settings)
    assert isinstance(actual.ocr_model, SuryaOCR)
