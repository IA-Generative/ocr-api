from pydantic_settings import BaseSettings, SettingsConfigDict


class PurgeSettings(BaseSettings):
    """Retention policy for the periodic task/file purge (Celery Beat)."""

    PURGE_ENABLED: bool = True
    TASK_RETENTION_DAYS: int = 365
    PURGE_BATCH_SIZE: int = 100
    # Interval, in seconds, between two purge runs. Defaults to once a day.
    PURGE_SCHEDULE_SECONDS: int = 86400

    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")
