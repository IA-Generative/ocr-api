from services.base.cache import BaseCache
from src.schemas.task import TaskModel, TaskStatus
from src.schemas.output import OCRResult


class MockeCache(BaseCache):
    def is_in_cache(self, task: TaskModel) -> bool:
        return task.content_hash == "1234"

    def get_task_from_cache(self, task: TaskModel) -> TaskModel:
        output_found = OCRResult(
            type="1",
            model_name="1",
            created_at=0,
            updated_at=1,
            version="1",
            total_pages=1,
            pages=[],
        )
        task.output = output_found
        return task


def test_is_in_cache():
    task = TaskModel(
        id="123",
        user_id="123",
        type="mock",
        status=TaskStatus.IN_PROGRESS,
        percentage=0,
        input=None,
        output=None,
        created_at=0,
        updated_at=1,
        extras={},
        content_hash="1234",
    )
    cache = MockeCache()
    assert cache.is_in_cache(task=task)


def test_update_task():
    task = TaskModel(
        id="123",
        user_id="123",
        type="mock",
        status=TaskStatus.IN_PROGRESS,
        percentage=0,
        input=None,
        output=None,
        created_at=0,
        updated_at=1,
        extras={},
        content_hash="1234",
    )
    output_found = OCRResult(
        type="1",
        model_name="1",
        created_at=0,
        updated_at=1,
        version="1",
        total_pages=1,
        pages=[],
    )
    cache = MockeCache()
    new_task = cache.get_task_from_cache(task=task)
    assert new_task.output == output_found
