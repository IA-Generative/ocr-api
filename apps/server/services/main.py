import os
import json
import traceback

import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

from services.base.pipeline import Pipeline
from src.config import SentrySettings
from src.connector.broker_connector import celery_app, celery_config
from src.logger import logger
from src.schemas.task import TaskForm, TaskModel, TaskStatus, task_table
from services.base.tracing import get_tracing_service
from .factory import load_worker

_sentry_settings = SentrySettings()
if _sentry_settings.SENTRY_WORKER_DSN:
    try:
        sentry_sdk.init(
            dsn=_sentry_settings.SENTRY_WORKER_DSN,
            send_default_pii=_sentry_settings.SEND_DEFAULT_PII,
            environment=os.getenv("ENVIRONMENT", "production"),
            integrations=[CeleryIntegration()],
        )
    except Exception as e:
        logger.warning(f"Sentry initialization failed, continuing without it: {e}")

process_ocr: Pipeline = load_worker(name=os.environ["PROCESS_NAME"])

logger.info(
    f"{os.environ['WORKER_NAME']} - {os.environ['PROCESS_NAME']} {celery_config.CELERY_APP_NAME}" + "\n" + 79 * "*"
)

tracing = get_tracing_service(tracing_name=os.environ.get("TRACING_SERVICE", "logging"))


@celery_app.task(name=os.environ["WORKER_NAME"], bind=True)
def launch_task(self, task_info: dict):
    task = TaskModel.model_validate(json.loads(task_info))
    with sentry_sdk.new_scope() as scope:
        scope.set_tag("task.id", task.id)
        scope.set_tag("worker.name", os.environ["WORKER_NAME"])
        scope.set_user({"id": task.user_id})
        return _run_task(task)


def _run_task(task: TaskModel) -> dict:
    try:
        with tracing.trace_context(trace_id=task.id, user_id=task.user_id, name=os.environ["WORKER_NAME"]):
            task = process_ocr.process(task=task)

        return task.model_dump()
    except Exception as e:
        task.extras = task.extras if task.extras else {}
        task.extras["error"] = str(e)
        task.extras["traceback"] = traceback.format_exc()
        task_table.update_task(
            task_id=task.id,
            form_data=TaskForm(
                user_id=task.user_id,
                type=task.type,
                status=TaskStatus.FAILED.value,
                extras=task.extras,
            ),
        )
        raise


if __name__ == "__main__":
    logger.info("Start to consume...")
    celery_app.start()
