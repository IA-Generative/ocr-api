import unittest
from unittest.mock import MagicMock
from pydantic import BaseModel
from typing import Any
from celery import Celery

from ocr_service.workers.base_worker import BaseWorker


class DummyTask(BaseModel):
    value: int


class DummyWorker(BaseWorker[DummyTask]):
    def process_task(self, task: DummyTask) -> DummyTask:
        return DummyTask(value=task.value * 2)


class TestBaseWorker(unittest.TestCase):
    def setUp(self):
        self.mock_celery_app = MagicMock(spec=Celery)

        def mock_task_decorator(name: str):
            def wrapper(func: Any):
                func.delay = MagicMock()
                func.apply_async = MagicMock()
                return func

            return wrapper

        self.mock_celery_app.task.side_effect = mock_task_decorator

        self.worker = DummyWorker(self.mock_celery_app, DummyTask)

    def test_delay_calls_celery(self):
        task = DummyTask(value=3)
        self.worker.delay(task)
        self.worker._celery_task.delay.assert_called_once_with({"value": 3})

    def test_apply_async_calls_celery(self):
        task = DummyTask(value=4)
        self.worker.apply_async(task, countdown=10)
        self.worker._celery_task.apply_async.assert_called_once_with(
            args=[{"value": 4}], countdown=10
        )

    def test_process_task_logic(self):
        result = self.worker.process_task(DummyTask(value=5))
        self.assertEqual(result.value, 10)

    def test_registered_task_calls_process_task(self):
        # Simule l’appel direct à la task enregistrée
        task_dict = {"value": 6}
        output = self.worker._celery_task(task_dict)
        self.assertEqual(output, {"value": 12})


if __name__ == "__main__":
    unittest.main()
