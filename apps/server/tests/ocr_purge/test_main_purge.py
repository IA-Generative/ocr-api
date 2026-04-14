import time
from datetime import datetime, timedelta
from ocr_purge.main import (
    get_cutoff_timestamp,
    chunked,
    fetch_eligible_tasks,
    STATUTS_SUPPRIMABLES,
    process_batch,
    main,
)
from src.schemas.task import TaskForm, TaskStatus
from src.services.task_service import task_table


def test_get_cutoff_timestamp():
    assert get_cutoff_timestamp(days=1) >= 3600 * 24


def test_chunked():
    actual = chunked([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], size=2)
    for batch in actual:
        assert len(batch) < 3


def test_fetch_eligible_tasks():
    new_task = task_table.insert_new_task(
        user_id="10", form_data=TaskForm(type="213", status=TaskStatus.CANCELED.value)
    )
    actuals = fetch_eligible_tasks(cutoff_ts=(datetime.now() + timedelta(seconds=3)).timestamp())
    find_id = False
    for task in actuals:
        assert task.status in STATUTS_SUPPRIMABLES
        if task.id == new_task.id:
            find_id = True

    assert find_id


def test_process_batch():
    new_task = task_table.insert_new_task(
        user_id="10", form_data=TaskForm(type="213", status=TaskStatus.CANCELED.value)
    )
    process_batch(batch=[new_task], dry_run=False)
    assert task_table.get_task_by_id(task_id=new_task.id) is None


def test_main_deletion():
    task_table.insert_new_task(user_id="10", form_data=TaskForm(type="213", status=TaskStatus.COMPLETED.value))
    time.sleep(1)
    delta = get_cutoff_timestamp(days=0, seconds=1)
    tasks_to_delete = fetch_eligible_tasks(cutoff_ts=delta)
    main(days=0, seconds=1)

    for task in tasks_to_delete:
        assert task_table.get_task_by_id(task_id=task.id) is None
