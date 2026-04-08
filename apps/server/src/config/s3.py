from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class S3Settings(BaseSettings):
    S3_BUCKET_NAME: str = "test"
    VERIFY_SSL: bool = False
    S3_PUBLIC_URL: Optional[str] = None  # Ex: https://storage.example.com en prod, http://localhost:9000 en dev
    AWS_ENDPOINT_URL: Optional[str] = None  # URL interne Docker (ex: http://minio:9000)
    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")

    @property
    def public_url(self) -> str:
        """URL publique pour les presigned URLs (priorité à S3_PUBLIC_URL, fallback sur AWS_ENDPOINT_URL)."""
        return (self.S3_PUBLIC_URL or self.AWS_ENDPOINT_URL or "http://localhost:9000").rstrip("/")
