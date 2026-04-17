import boto3
from services.client.server import ServerClient
from src.connector.s3_connector import S3Connector, s3_settings
from src.config.openai import OpenAISettings
import openai

openai_settings = OpenAISettings()
file_connector = S3Connector(
    s3_client=boto3.client("s3", verify=s3_settings.VERIFY_SSL),
    bucket_name=s3_settings.S3_BUCKET_NAME,
)


server_client = ServerClient()

openai_client = openai.OpenAI(api_key=openai_settings.OPENAI_API_KEY, base_url=openai_settings.OPENAI_BASE_URL)
