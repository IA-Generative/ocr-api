import boto3

from src.connector import S3Connector, s3_settings

s3_client = boto3.client("s3", verify=s3_settings.VERIFY_SSL)
s3_client_connector = S3Connector(s3_client=s3_client, bucket_name=s3_settings.AWS_BUCKET_NAME)
