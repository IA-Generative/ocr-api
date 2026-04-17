from celery.signals import task_failure, task_success, task_revoked, task_unknown
from celery import Task
from billiard.einfo import ExceptionInfo
from src.logger import logger
from services.client.tools import server_client
from src.schemas.task import TaskStatus


@task_failure.connect
def task_failure_handler(
    task_id: str | None,
    exception: Exception | None,
    traceback,
    einfo: ExceptionInfo | None,
    *args,
    **kwargs,
):
    logger.error(f"Task {task_id} failed with exception: {exception}")
    logger.error(f"Traceback: {traceback}")
    args = args or []
    logger.debug(f"Task {task_id} args: {args}")
    if task_id:
        server_client.update_task_by_id(
            task_id=task_id,
            task_type="unknown",
            update_data={
                "status": TaskStatus.FAILED.value,
                "extras": {"error": str(exception), "traceback": str(traceback)},
            },
        )
        logger.info(f"Updated task {task_id} status to FAILED in server client.")


@task_success.connect
def task_success_handler(sender: Task, **kwargs):
    logger.info(f"Task {sender.request.id} completed successfully with result: {kwargs.get('result')}")
    if sender.request.id:
        server_client.update_task_by_id(
            task_id=sender.request.id,
            task_type="unknown",
            update_data={"status": TaskStatus.COMPLETED.value, "percentage": 1},
        )


@task_revoked.connect
def task_revoked_handler(sender: Task, request, terminated, signum, expired, **kwargs):
    logger.warning(f"Task {request.id} was revoked. Terminated: {terminated}, Signum: {signum}, Expired: {expired}")
    if request.id:
        server_client.update_task_by_id(
            task_id=request.id,
            task_type="unknown",
            update_data={"status": TaskStatus.REVOKED.value},
        )


@task_unknown.connect
def task_unknown_handler(sender: Task, request, **kwargs):
    logger.warning(f"Received unknown task: {request.id} with name: {request.name}")
    if request.id:
        server_client.update_task_by_id(
            task_id=request.id,
            task_type="unknown",
            update_data={
                "status": TaskStatus.FAILED.value,
                "extras": {"error": "Received unknown task type."},
            },
        )
