"""Periodic purge of old tasks (DB rows + their S3 files), scheduled via Celery Beat.

Uses a crontab schedule rather than a plain interval, per
https://docs.celeryq.dev/en/4.0/userguide/periodic-tasks.html#crontab-schedules.
Retention/scheduling are read from `PurgeSettings` (see docs/variables.md):
`TASK_RETENTION_DAYS`, `PURGE_BATCH_SIZE`, `PURGE_CRON_*`, `PURGE_ENABLED`.
"""

from datetime import datetime, timedelta

from celery.schedules import crontab

from src.config import PurgeSettings
from src.connector.broker_connector import celery_app
from src.logger import logger
from src.schemas.task import TaskStatus, task_table

from .connectors import s3_client_connector

purge_settings = PurgeSettings()

# Only terminal statuses are eligible: a task still queued/started/in_progress/retrying
# must never be purged out from under itself, regardless of age.
PURGEABLE_STATUSES = [
    TaskStatus.COMPLETED,
    TaskStatus.FAILED,
    TaskStatus.CANCELED,
    TaskStatus.TIMEOUT,
]


@celery_app.task(name="ocr_backend.purge_old_tasks")
def purge_old_tasks() -> int:
    """Delete every terminal task older than `TASK_RETENTION_DAYS`, and its S3 file(s).

    Returns the number of tasks deleted.
    """
    cutoff_date = datetime.now() - timedelta(days=purge_settings.TASK_RETENTION_DAYS)
    deleted_tasks = task_table.delete_tasks_created_before(
        cutoff_date=cutoff_date,
        statuses=PURGEABLE_STATUSES,
        batch_size=purge_settings.PURGE_BATCH_SIZE,
    )

    for task in deleted_tasks:
        try:
            s3_client_connector.delete_by_task_id(user_id=task.user_id, task_id=task.id)
        except Exception as e:
            logger.error(f"[purge_old_tasks] Failed to delete S3 file(s) for task {task.id}: {e}")

    logger.info(
        f"[purge_old_tasks] Deleted {len(deleted_tasks)} task(s) created before "
        f"{cutoff_date.isoformat()} ({purge_settings.TASK_RETENTION_DAYS} day(s) retention)."
    )
    return len(deleted_tasks)


if purge_settings.PURGE_ENABLED:
    celery_app.conf.beat_schedule = {
        **(celery_app.conf.beat_schedule or {}),
        "purge-old-tasks": {
            "task": "ocr_backend.purge_old_tasks",
            "schedule": crontab(
                minute=purge_settings.PURGE_CRON_MINUTE,
                hour=purge_settings.PURGE_CRON_HOUR,
                day_of_week=purge_settings.PURGE_CRON_DAY_OF_WEEK,
                day_of_month=purge_settings.PURGE_CRON_DAY_OF_MONTH,
                month_of_year=purge_settings.PURGE_CRON_MONTH_OF_YEAR,
            ),
        },
    }
