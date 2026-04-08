import pytest
import openai
from pathlib import Path

from src.connector import S3Connector, s3_settings
import boto3


@pytest.fixture
def openai_client() -> openai.Client:
    return openai.Client(base_url="http://localhost:5000/v1", api_key="secret-api")


@pytest.fixture
def s3_connector() -> S3Connector:
    s3_client = boto3.client("s3", verify=s3_settings.VERIFY_SSL)
    s3_client_connector = S3Connector(s3_client=s3_client, bucket_name=s3_settings.S3_BUCKET_NAME)
    return s3_client_connector


@pytest.fixture
def test_image_url(s3_connector: S3Connector) -> tuple[Path, str]:
    path = Path("tests/data/valid/identite.jpg")
    s3_key = s3_connector.save(user_id="test_user", task_id="test_task", file_path=str(path))
    return path, s3_connector.generate_presigned_url(s3_key)


def test_models_stream_integration(openai_client: openai.Client):
    models = openai_client.models
    assert models is not None
    assert hasattr(models, "list")


def test_chat_completion_integration(openai_client: openai.Client, test_image_url: tuple[Path, str]):
    """
    Test the full flow of sending a chat completion request with an image, and receiving the extracted text.

    This test assumes the OCR service is running and accessible at the configured base URL.

    When stream=false the response is a standard ChatCompletion object containing the final result.
    """
    _, s3_public_url = test_image_url
    response = openai_client.chat.completions.create(
        model="ocr-v1",
        stream=False,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract text from this image."},
                    {
                        "type": "image_url",
                        "image_url": {"url": s3_public_url},
                    },
                ],
            }
        ],
    )

    data = response.model_dump()
    assert "choices" in data
    assert len(data["choices"]) == 1
    message = data["choices"][0]["message"]
    assert message["role"] == "assistant"
    assert "content" in message
    # Further assertions can be made on the content format and extracted text depending on the expected output
