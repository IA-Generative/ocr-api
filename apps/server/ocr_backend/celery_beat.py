"""Entrypoint for the Celery Beat scheduler process.

Run as: `celery -A ocr_backend.celery_beat:celery_app beat`.

Importing `.purge` registers the `purge_old_tasks` task and its beat schedule entry
on `celery_app` as a side effect; `celery beat` only needs this module to know what
to schedule, it never executes the task itself (a worker subscribed to the queue does).
"""

from src.connector.broker_connector import celery_app

from . import purge  # noqa: F401

__all__ = ["celery_app"]
