import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from src.schemas import Base
from src.schemas.input import InputForm
from src.schemas.task import (
    TaskTable,
    TaskForm,
    TaskUpdateForm,
    TaskOperation,
    TaskStatus,
)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def task_table(db_session) -> TaskTable:
    @contextmanager
    def fake_get_db():
        yield db_session

    return TaskTable(get_db=fake_get_db)


def test_insert_new_task(task_table: TaskTable):
    form_data = TaskForm(
        user_id="user123",
        type="classification",
        status=TaskStatus.QUEUED.value,
        percentage=10.5,
        extras={"source": "test"},
    )

    # Appelle la méthode
    result = task_table.insert_new_task(user_id="user123", form_data=form_data)

    assert result is not None
    assert result.user_id == "user123"
    assert result.type == "classification"
    assert result.status == TaskStatus.QUEUED.value
    assert result.percentage == 10.5
    assert result.extras["source"] == "test"
    assert isinstance(result.created_at, int)
    assert isinstance(result.updated_at, int)


def test_insert_new_task_w_input(task_table: TaskTable):
    form_data = TaskForm(
        user_id="user123",
        type="classification",
        status=TaskStatus.QUEUED.value,
        input=InputForm(
            type="image",
            storage_file_path="https://example.com/image.jpg",
            raw_filename="image.jpg",
            content_type="image/jpeg",
            ext=".jpg",
            size=123456,
        ),
        percentage=10.5,
        extras={"source": "test"},
    )

    # Appelle la méthode
    result = task_table.insert_new_task(user_id="user123", form_data=form_data)

    assert result is not None
    assert result.user_id == "user123"
    assert result.type == "classification"
    assert result.status == TaskStatus.QUEUED.value
    assert result.percentage == 10.5
    assert result.extras["source"] == "test"
    assert isinstance(result.created_at, int)
    assert isinstance(result.updated_at, int)
    assert result.input is not None


def test_update_task(task_table: TaskTable):
    new_task = task_table.insert_new_task(
        user_id="user456",
        form_data=TaskForm(
            user_id="user456",
            type=TaskOperation.OCR.value,
            status=TaskStatus.QUEUED.value,
            percentage=0.0,
            extras={"initial": True},
        ),
    )

    assert new_task is not None

    update_form = TaskUpdateForm(status="done", percentage=100.0, extras={"updated": True})

    updated = task_table.update_task(task_id=new_task.id, form_data=update_form)

    assert updated is not None
    assert updated.id == new_task.id
    assert updated.status == "done"
    assert updated.percentage == 100.0
    assert updated.extras == {"updated": True}

    not_found_updated = task_table.update_task(task_id="zzz", form_data=update_form)
    assert not_found_updated is None


def test_update_task_w_input(task_table: TaskTable):
    input_form = InputForm(
        type="image",
        storage_file_path="https://example.com/image.jpg",
        raw_filename="image.jpg",
        content_type="image/jpeg",
        ext=".jpg",
        size=123456,
    )

    new_task = task_table.insert_new_task(
        user_id="user456",
        form_data=TaskForm(
            user_id="user456",
            type=TaskOperation.OCR.value,
            status=TaskStatus.QUEUED.value,
            input=input_form,
            percentage=0.0,
            extras={"initial": True},
        ),
    )

    assert new_task is not None

    update_form = TaskUpdateForm(status="done", percentage=100.0, extras={"updated": True})

    updated = task_table.update_task(task_id=new_task.id, form_data=update_form)

    assert updated is not None
    assert updated.id == new_task.id
    assert updated.status == "done"
    assert updated.percentage == 100.0
    assert updated.extras == {"updated": True}

    not_found_updated = task_table.update_task(task_id="zzz", form_data=update_form)
    assert not_found_updated is None
    assert updated.input == input_form


def test_get_task_by_id(task_table: TaskTable):
    # Step 1: Insert a task
    task = task_table.insert_new_task(
        user_id="user789",
        form_data=TaskForm(
            user_id="user789",
            type="detection",
            status=TaskStatus.QUEUED.value,
            percentage=0.0,
            extras={"test": True},
        ),
    )

    assert task is not None

    # Step 2: Retrieve it
    retrieved = task_table.get_task_by_id(task.id)

    # Step 3: Assertions
    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.type == "detection"
    assert retrieved.status == TaskStatus.QUEUED.value


def test_get_tasks_by_id(task_table: TaskTable):
    # Step 1: Insert a task
    task = task_table.insert_new_task(
        user_id="user789",
        form_data=TaskForm(
            user_id="user789",
            type="detection",
            status=TaskStatus.QUEUED.value,
            percentage=0.0,
            extras={"test": True},
        ),
    )

    assert task is not None

    # Step 2: Retrieve it
    retrieved = task_table.get_tasks_by_id(task.id)

    # Step 3: Assertions
    assert retrieved is not None
    assert len(retrieved) == 1
    assert retrieved[0].id == task.id
    assert retrieved[0].type == "detection"
    assert retrieved[0].status == TaskStatus.QUEUED.value
    retrieved = task_table.get_tasks_by_id("task.id")
    assert retrieved is None


def test_get_tasks_by_pks(task_table: TaskTable):
    # Step 1: Insert a task
    task = task_table.insert_new_task(
        user_id="user789",
        form_data=TaskForm(
            user_id="user789",
            type="detection",
            status=TaskStatus.QUEUED.value,
            percentage=0.0,
            extras={"test": True},
        ),
    )

    assert task is not None

    # Step 2: Retrieve it
    retrieved = task_table.get_task_by_pks(task.id, task_type="detection")
    # Step 3: Assertions
    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.type == "detection"
    assert retrieved.status == TaskStatus.QUEUED.value
    retrieved = task_table.get_task_by_pks(task.id, task_type="detectionnot-found")
    assert retrieved is None


def test_get_task_by_invalid_id(task_table: TaskTable):
    result = task_table.get_task_by_id("non-existent-id")
    assert result is None


def test_delete_task_by_id(task_table: TaskTable):
    # Step 1: Create a task
    task = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(
            user_id="user123",
            type="task_type",
            status=TaskStatus.QUEUED.value,
            percentage=50.0,
            extras={"key": "value"},
        ),
    )

    assert task is not None

    # Step 2: Delete the task by id
    deleted_task = task_table.delete_task_by_id(task.id)

    # Step 3: Assertions
    assert deleted_task is not None
    assert deleted_task.id == task.id  # Ensure it's the same task

    # Step 4: Check that the task is deleted (it should return None now)
    task_after_deletion = task_table.get_task_by_id(task.id)
    assert task_after_deletion is None

    not_found_deleted_task = task_table.delete_task_by_id("task.id")
    assert not_found_deleted_task is None


def test_get_tasks_by_user_id_with_pagination(task_table: TaskTable):
    # Step 1: Insert 15 tasks for user123
    for i in range(15):
        task_table.insert_new_task(
            user_id="user123",
            form_data=TaskForm(
                user_id="user123",
                type=f"task_type_{i}",
                status=TaskStatus.QUEUED.value,
                percentage=50.0,
                extras={"key": f"value_{i}"},
            ),
        )

    # Step 2: Retrieve first page with 5 tasks per page
    tasks_page_1 = task_table.get_tasks_by_user_id(user_id="user123", page=1, page_size=5)
    assert tasks_page_1 is not None
    assert len(tasks_page_1) == 5  # First page should contain 5 tasks

    # Step 3: Retrieve second page with 5 tasks per page
    tasks_page_2 = task_table.get_tasks_by_user_id(user_id="user123", page=2, page_size=5)
    assert tasks_page_2 is not None
    assert len(tasks_page_2) == 5  # Second page should also contain 5 tasks

    # Step 4: Retrieve third page with 5 tasks per page (which should be the last page)
    tasks_page_3 = task_table.get_tasks_by_user_id(user_id="user123", page=3, page_size=5)
    assert tasks_page_3 is not None

    assert len(tasks_page_3) == 5  # Last page should also contain 5 tasks


def test_delete_tasks_by_user_id(task_table: TaskTable):
    # Step 1: Insert 5 tasks for user123
    for i in range(5):
        task_table.insert_new_task(
            user_id="user1234",
            form_data=TaskForm(
                user_id="user123",
                type=f"task_type_{i}",
                status=TaskStatus.QUEUED.value,
                percentage=50.0,
                extras={"key": f"value_{i}"},
            ),
        )

    # Step 2: Delete all tasks for user123
    deleted_tasks = task_table.delete_tasks_by_user_id("user1234")

    # Step 3: Assertions
    assert deleted_tasks is not None
    assert len(deleted_tasks) == 5  # All tasks should be deleted

    # Step 4: Verify that tasks are actually deleted (should return None when trying to get them)
    tasks_after_deletion = task_table.get_tasks_by_user_id(user_id="user1234", page=1, page_size=10)
    assert tasks_after_deletion is None or len(tasks_after_deletion) == 0  # No tasks left for this user

    no_deleted_tasks = task_table.delete_tasks_by_user_id("user1234")
    assert no_deleted_tasks is None


def test_get_task_by_hash_content(task_table: TaskTable):
    task = task_table.insert_new_task(
        user_id="user1234",
        form_data=TaskForm(
            user_id="user123",
            type="task_type_0",
            status=TaskStatus.QUEUED.value,
            percentage=50.0,
            extras={"key": "value_0"},
            content_hash="1111",
        ),
    )
    found_task = task_table.get_task_by_content_hash(content_hash_value=task.content_hash)
    assert task.content_hash == found_task.content_hash
