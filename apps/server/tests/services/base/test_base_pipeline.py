from unittest.mock import MagicMock


from services.base.pipeline import Pipeline
from services.base.worker import BaseWorker
from src.schemas.task import TaskModel


def make_task() -> TaskModel:
    return TaskModel(
        id="task-1",
        user_id="user-1",
        type="ocr",
        status="queued",
        created_at=0,
        updated_at=0,
    )


def make_worker(name: str, is_applicable: bool) -> MagicMock:
    worker = MagicMock(spec=BaseWorker)
    worker.name = name
    worker.is_applicable.return_value = is_applicable
    worker.process_task.side_effect = lambda task: task
    return worker


def test_pipeline_uses_first_applicable_worker():
    task = make_task()
    w1 = make_worker("w1", is_applicable=False)
    w2 = make_worker("w2", is_applicable=True)
    w3 = make_worker("w3", is_applicable=True)

    pipeline = Pipeline(workers=[w1, w2, w3])
    pipeline.process(task)

    w1.process_task.assert_not_called()
    w2.process_task.assert_called_once_with(task)
    w3.process_task.assert_not_called()


def test_pipeline_returns_task_unchanged_when_no_worker_applicable():
    task = make_task()
    w1 = make_worker("w1", is_applicable=False)
    w2 = make_worker("w2", is_applicable=False)

    pipeline = Pipeline(workers=[w1, w2])
    result = pipeline.process(task)

    assert result == task
    w1.process_task.assert_not_called()
    w2.process_task.assert_not_called()


def test_pipeline_returns_task_when_workers_list_is_empty():
    task = make_task()
    pipeline = Pipeline(workers=[])
    result = pipeline.process(task)
    assert result == task


def test_pipeline_returns_processed_task():
    task = make_task()
    processed_task = make_task()
    processed_task = processed_task.model_copy(update={"status": "done"})

    worker = make_worker("w1", is_applicable=True)
    worker.process_task.return_value = processed_task

    pipeline = Pipeline(workers=[worker])
    result = pipeline.process(task)

    assert result.status == "queued"
