import os 
from unittest.mock import patch

from ocr_backend.clients import minio_connector
from src.schemas.task import task_table, TaskForm, TaskModel, TaskStatus
import json


def test_task_process_surya():
    os.environ['MODEL_NAME'] = "surya"
    from ocr_service.main import launch_task
    user_id = "test"
    task = task_table.insert_new_task(user_id=user_id, form_data=TaskForm(
        user_id=user_id, type="OCR", status=TaskStatus.CREATED.value, percentage=0, extras={}))

    saved_path = minio_connector.save(user_id=user_id, task_id=task.id,
                                      file_path="tests/data/valid/cerfa_13750-05-1.pdf")

    task.extras.update({
        "file_path": saved_path,
        "raw_filename": 'tests/data/valid/cerfa_13750-05-1.pdf',
        "content_type": "application/pdf",
        "ext": ".pdf",
    })
        
    result = launch_task.apply(args=(json.dumps(task.model_dump()),))
    result = result.get()
    actual = TaskModel.model_validate(result)
    assert actual.id == task.id
    assert actual.status == TaskStatus.COMPLETED.value

def test_task_process_paddle():
    os.environ['MODEL_NAME'] = "paddle"
    from ocr_service.main import launch_task
    user_id = "test"
    task = task_table.insert_new_task(user_id=user_id, form_data=TaskForm(
        user_id=user_id, type="OCR", status=TaskStatus.CREATED.value, percentage=0, extras={}))

    saved_path = minio_connector.save(user_id=user_id, task_id=task.id,
                                      file_path="tests/data/valid/cerfa_13750-05-1.pdf")

    task.extras.update({
        "file_path": saved_path,
        "raw_filename": 'tests/data/valid/cerfa_13750-05-1.pdf',
        "content_type": "application/pdf",
        "ext": ".pdf",
    })
        
    result = launch_task.apply(args=(json.dumps(task.model_dump()),))
    result = result.get()
    actual = TaskModel.model_validate(result)
    assert actual.id == task.id
    assert actual.status == TaskStatus.COMPLETED.value