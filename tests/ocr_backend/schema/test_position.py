import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from src.schemas import Base
from src.schemas.task import Task, TaskStatus, TaskTable
from tests.src.schemas.test_task_table import task_table, db_session



def test_task_not_found(task_table):
    assert task_table.get_position_in_queue("non_existent_id") is None


def test_task_not_in_queue(task_table, db_session):
    now = int(datetime.now().timestamp())
    task = Task(
        id="t1",
        type="ocr",
        user_id="t1",
        percentage=0.0,
        status=TaskStatus.COMPLETED,
        created_at=now - 30,
    )
    db_session.add(task)
    db_session.commit()
    assert task_table.get_position_in_queue("t1") is None


def test_task_in_queue_position_zero(task_table, db_session):
    now = int(datetime.now().timestamp())
    task = Task(
        id="t1",
        type="ocr",
        user_id="t1",
        percentage=0.0,
        status=TaskStatus.QUEUED,
        created_at=now,
    )
    db_session.add(task)
    db_session.commit()
    assert task_table.get_position_in_queue("t1") == 0


def test_task_in_queue_position_two(task_table, db_session):
    now = int(datetime.now().timestamp())
    task1 = Task(
        id="t1",
        type="ocr",
        user_id="t1",
        percentage=0.0,
        status=TaskStatus.QUEUED,
        created_at=now - 30,
    )
    task2 = Task(
        id="t2",
        type="ocr",
        user_id="t2",
        percentage=0.0,
        status=TaskStatus.QUEUED,
        created_at=now - 20,
    )
    task3 = Task(id="t3", type="ocr", user_id="t3", percentage=0.0, status=TaskStatus.QUEUED, created_at=now)

    db_session.add_all([task1, task2, task3])
    db_session.commit()

    assert task_table.get_position_in_queue("t3") == 2
    assert task_table.get_position_in_queue("t2") == 1
    assert task_table.get_position_in_queue("t1") == 0
