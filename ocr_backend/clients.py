from src.config.fs import FileSystemSettings
from src.config.minio import MinioSettings
from src.connector.fs import FileSystemConnector
from src.connector.minio_connector import MinioConnector
from minio import Minio
from src.schemas.health import Health, HealthError
from src import __version__
from datetime import datetime
import minio

health_check = []
up_time = datetime.now().isoformat()
try:
    fs_settings = FileSystemSettings()
    fs_connector = FileSystemConnector(base_folder=fs_settings.FOLDER)
    health = Health(name="fs_connector", version=__version__,
                    up_time=up_time, status="healthy")

except Exception as e:
    health = HealthError(name="fs_connector", error=str(e), code_status=500)

health_check.append(health)

try:
    minio_settings = MinioSettings()
    minio_client = Minio(endpoint=minio_settings.MINIO_END_POINT,
                         access_key=minio_settings.MINIO_ACCESS_KEY, secret_key=minio_settings.MINIO_SECRET_KEY, secure=False)

    minio_connector = MinioConnector(
        minio_client=minio_client, bucket_name=minio_settings.MINIO_BUCKET_NAME)
    health = Health(name="minio_connector", version=minio.__version__,
                    up_time=up_time, status="healthy")

except Exception as e:
    health = HealthError(name="minio_connector", error=str(e), code_status=500)


health_check.append(health)
