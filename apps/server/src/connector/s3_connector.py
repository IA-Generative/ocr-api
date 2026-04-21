import tempfile
import datetime

import aioboto3
import boto3
from botocore.exceptions import ClientError

from ..config.s3 import S3Settings
from ..schemas.health import Health
from .base import BaseFileConnector
from ..logger import logger
import re

from boto3.s3.transfer import TransferConfig

config = TransferConfig(
    multipart_threshold=8 * 1024 * 1024,  # fichiers >8MB en multipart
    max_concurrency=2,  # nombre de threads
    multipart_chunksize=8 * 1024 * 1024,  # taille des chunks
    use_threads=True,
)


class S3Connector(BaseFileConnector):
    def __init__(self, s3_client: boto3.client = None, bucket_name: str = "mybucket"):
        super().__init__()
        self.client = s3_client or boto3.client("s3")
        self.bucket_name = bucket_name
        self.up_time = datetime.datetime.now().isoformat()

        self._settings = S3Settings()
        self._public_client = boto3.client(
            "s3",
            endpoint_url=self._settings.public_url,
        )

        # aioboto3 session (créée une seule fois, thread-safe)
        self._aio_session = aioboto3.Session()

        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = int(e.response["Error"]["Code"])
            if error_code == 404:
                self.client.create_bucket(Bucket=self.bucket_name)
            else:
                raise e

    @staticmethod
    def extract_key_from_url(
        url: str,
        bucket_name: str,
        s3_endpoint: str,
    ) -> str:
        # Match /<bucket_name>/<key> regardless of the hostname (handles localhost vs minio mismatches)
        pattern = rf"/{re.escape(bucket_name)}/([^?]+)"
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return url

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL using the public-facing endpoint (browser-accessible)."""
        return self._public_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )

    def get_by_task_id(self, user_id: str, task_id: str) -> str:
        object_key = f"{user_id}/{task_id}"
        try:
            metadata = self.client.head_object(Bucket=self.bucket_name, Key=object_key)
            logger.debug(f"{task_id} - {metadata['ContentLength']}")
            tmp_file = tempfile.NamedTemporaryFile(delete=False)
            tmp_file_path = tmp_file.name
            tmp_file.close()  # Important, boto3 va l’écrire
            logger.debug(f"{task_id} - Start to save chunk")
            self.client.download_file(self.bucket_name, object_key, tmp_file_path, Config=config)

            return tmp_file_path
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"{object_key} non trouvé : {e}")
            raise FileNotFoundError(f"{object_key} non trouvé : {e}")

        except Exception as e:
            raise e

    def save(self, user_id: str, task_id: str, file_path: str) -> str:
        object_key = f"{user_id}/{task_id}"
        try:
            self.client.upload_file(file_path, self.bucket_name, object_key)
            return object_key
        except ClientError as e:
            raise Exception(f"Erreur lors de la sauvegarde du fichier : {e}")

    def delete_by_task_id(self, user_id: str, task_id: str) -> bool:
        object_key = f"{user_id}/{task_id}"
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"Fichier non trouvé pour la tâche {task_id} de l'utilisateur {user_id} : {e}")
            else:
                raise e

    def get_health(self) -> Health:
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except Exception as error:
            return Health(
                name="s3",
                extras={"error": str(error)},
                version=boto3.__version__,
                up_time=self.up_time,
                status="unhealthy",
            )
        return Health(name="s3", version=boto3.__version__, up_time=self.up_time, status="healthy")

    def delete_by_user_id(self, user_id: str) -> bool:
        batch_delete_size: int = 1_000
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix=f"{user_id}/")

            delete_us = dict(Objects=[])
            for page in pages:
                for obj in page.get("Contents", []):
                    delete_us["Objects"].append(dict(Key=obj["Key"]))
                    if len(delete_us["Objects"]) >= batch_delete_size:
                        self.client.delete_objects(Bucket=self.bucket_name, Delete=delete_us)
                        delete_us = dict(Objects=[])

            if delete_us["Objects"]:
                self.client.delete_objects(Bucket=self.bucket_name, Delete=delete_us)

            return True
        except ClientError as e:
            raise Exception(f"Erreur lors de la suppression des fichiers pour l'utilisateur {user_id} : {e}")

    # ── Async native (aioboto3) ──

    def _aio_client(self):
        """Context manager for an async S3 client using the internal endpoint."""
        return self._aio_session.client(
            "s3",
            endpoint_url=self._settings.AWS_ENDPOINT_URL,
            verify=self._settings.VERIFY_SSL,
        )

    def _aio_public_client(self):
        """Context manager for an async S3 client using the public endpoint (presigned URLs)."""
        return self._aio_session.client(
            "s3",
            endpoint_url=self._settings.public_url,
        )

    async def asave(self, user_id: str, task_id: str, file_path: str) -> str:
        object_key = f"{user_id}/{task_id}"
        async with self._aio_client() as s3:
            await s3.upload_file(file_path, self.bucket_name, object_key)
        return object_key

    async def aget_by_task_id(self, user_id: str, task_id: str) -> str:
        object_key = f"{user_id}/{task_id}"
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file_path = tmp_file.name
        tmp_file.close()
        async with self._aio_client() as s3:
            await s3.download_file(self.bucket_name, object_key, tmp_file_path)
        return tmp_file_path

    async def adelete_by_task_id(self, user_id: str, task_id: str) -> bool:
        object_key = f"{user_id}/{task_id}"
        async with self._aio_client() as s3:
            await s3.delete_object(Bucket=self.bucket_name, Key=object_key)
        return True

    async def adelete_by_user_id(self, user_id: str) -> bool:
        batch_delete_size = 1_000
        async with self._aio_client() as s3:
            paginator = s3.get_paginator("list_objects_v2")
            delete_us: dict = dict(Objects=[])
            async for page in paginator.paginate(Bucket=self.bucket_name, Prefix=f"{user_id}/"):
                for obj in page.get("Contents", []):
                    delete_us["Objects"].append(dict(Key=obj["Key"]))
                    if len(delete_us["Objects"]) >= batch_delete_size:
                        await s3.delete_objects(Bucket=self.bucket_name, Delete=delete_us)
                        delete_us = dict(Objects=[])
            if delete_us["Objects"]:
                await s3.delete_objects(Bucket=self.bucket_name, Delete=delete_us)
        return True

    async def aget_object(self, key: str) -> bytes:
        """Download an object's body from S3 asynchronously."""
        async with self._aio_client() as s3:
            resp = await s3.get_object(Bucket=self.bucket_name, Key=key)
            body = await resp["Body"].read()
        return body

    async def agenerate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL using the public-facing async client."""
        async with self._aio_public_client() as s3:
            url = await s3.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
        return url

    async def aget_health(self) -> Health:
        try:
            async with self._aio_client() as s3:
                await s3.head_bucket(Bucket=self.bucket_name)
        except Exception as error:
            return Health(
                name="s3",
                extras={"error": str(error)},
                version=boto3.__version__,
                up_time=self.up_time,
                status="unhealthy",
            )
        return Health(name="s3", version=boto3.__version__, up_time=self.up_time, status="healthy")


s3_settings = S3Settings()
