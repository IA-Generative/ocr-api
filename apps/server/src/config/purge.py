from pydantic_settings import BaseSettings, SettingsConfigDict


class PurgeSettings(BaseSettings):
    """Retention policy for the periodic task/file purge (Celery Beat)."""

    PURGE_ENABLED: bool = True
    TASK_RETENTION_DAYS: int = 365
    PURGE_BATCH_SIZE: int = 100
    # Crontab fields for the Celery Beat schedule (celery.schedules.crontab), see
    # https://docs.celeryq.dev/en/4.0/userguide/periodic-tasks.html#crontab-schedules.
    # Default: every day at 02:00, off-peak hours.
    PURGE_CRON_MINUTE: str = "0"
    PURGE_CRON_HOUR: str = "2"
    PURGE_CRON_DAY_OF_WEEK: str = "*"
    PURGE_CRON_DAY_OF_MONTH: str = "*"
    PURGE_CRON_MONTH_OF_YEAR: str = "*"

    model_config = SettingsConfigDict(from_attributes=True, case_sensitive=True, env_file=".env", extra="allow")
