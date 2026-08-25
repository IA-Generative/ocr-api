import json
from contextlib import contextmanager

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import src.schemas.task as task_module
from src.connector.encryption.local_provider import LocalEncryptionProvider
from src.schemas import Base
from src.schemas.output import OCRResult, Page
from src.schemas.task import TaskForm, TaskOperation, TaskStatus, TaskTable, TaskUpdateForm

SENSITIVE_TEXT = "Contenu sensible extrait du document"


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


@pytest.fixture
def encryption_provider(monkeypatch):
    # Provider déterministe pour les tests, isolé de tout ENCRYPTION_KEY d'environnement.
    provider = LocalEncryptionProvider(key=LocalEncryptionProvider.generate_key())
    monkeypatch.setattr(task_module, "_get_encryption_provider", lambda: provider)
    return provider


def _sample_output() -> OCRResult:
    return OCRResult(
        type="ocr",
        model_name="test-model",
        created_at=0,
        updated_at=0,
        version="1.0",
        total_pages=1,
        pages=[Page(page=1)],
        text=SENSITIVE_TEXT,
    )


def _raw_output(db_session, task_id: str) -> dict:
    raw_task = db_session.query(task_module.Task).filter(task_module.Task.id == task_id).first()
    return raw_task.output


def test_insert_new_task_encrypts_output_at_rest(task_table, db_session, encryption_provider):
    form_data = TaskForm(
        user_id="user123",
        type=TaskOperation.OCR.value,
        status=TaskStatus.QUEUED.value,
        output=_sample_output(),
    )

    result = task_table.insert_new_task(user_id="user123", form_data=form_data)

    # Le format renvoyé par l'API ne change pas : toujours un OCRResult en clair.
    assert result.output.text == SENSITIVE_TEXT

    # Ce qui est effectivement écrit en base est chiffré, sous enveloppe.
    stored_output = _raw_output(db_session, result.id)
    assert stored_output["__enc__"] == "v1"
    assert SENSITIVE_TEXT not in json.dumps(stored_output)


def test_get_task_by_id_decrypts_output(task_table, encryption_provider):
    created = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(
            user_id="user123",
            type=TaskOperation.OCR.value,
            status=TaskStatus.QUEUED.value,
            output=_sample_output(),
        ),
    )

    fetched = task_table.get_task_by_id(created.id)

    assert fetched.output.text == SENSITIVE_TEXT


def test_get_tasks_by_user_id_decrypts_output(task_table, encryption_provider):
    task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(
            user_id="user123",
            type=TaskOperation.OCR.value,
            status=TaskStatus.QUEUED.value,
            output=_sample_output(),
        ),
    )

    tasks = task_table.get_tasks_by_user_id(user_id="user123", page=1, page_size=10)

    assert tasks[0].output.text == SENSITIVE_TEXT


def test_delete_task_by_id_decrypts_output(task_table, encryption_provider):
    created = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(
            user_id="user123",
            type=TaskOperation.OCR.value,
            status=TaskStatus.QUEUED.value,
            output=_sample_output(),
        ),
    )

    deleted = task_table.delete_task_by_id(created.id)

    assert deleted.output.text == SENSITIVE_TEXT


def test_update_task_encrypts_and_returns_plaintext_output(task_table, db_session, encryption_provider):
    created = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(user_id="user123", type=TaskOperation.OCR.value, status=TaskStatus.QUEUED.value),
    )

    updated = task_table.update_task(
        task_id=created.id,
        form_data=TaskUpdateForm(status="completed", output=_sample_output()),
    )

    assert updated.output.text == SENSITIVE_TEXT

    stored_output = _raw_output(db_session, created.id)
    assert stored_output["__enc__"] == "v1"


def test_update_task_without_output_keeps_previous_output_decrypted(task_table, encryption_provider):
    created = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(
            user_id="user123",
            type=TaskOperation.OCR.value,
            status=TaskStatus.QUEUED.value,
            output=_sample_output(),
        ),
    )

    updated = task_table.update_task(task_id=created.id, form_data=TaskUpdateForm(status="completed"))

    assert updated.output.text == SENSITIVE_TEXT


def test_legacy_plaintext_output_still_readable(task_table, db_session, encryption_provider):
    # Simule une ligne écrite avant l'activation du chiffrement : output en clair, sans enveloppe.
    legacy_task = task_module.Task(
        id="legacy-task-id",
        type=TaskOperation.OCR.value,
        status=TaskStatus.COMPLETED.value,
        user_id="user123",
        percentage=100.0,
        output=_sample_output().model_dump(),
        created_at=0,
        updated_at=0,
    )
    db_session.add(legacy_task)
    db_session.commit()

    fetched = task_table.get_task_by_id("legacy-task-id")

    assert fetched.output.text == SENSITIVE_TEXT


def test_insert_new_task_flags_output_encrypted(task_table, encryption_provider):
    with_output = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(
            user_id="user123",
            type=TaskOperation.OCR.value,
            status=TaskStatus.QUEUED.value,
            output=_sample_output(),
        ),
    )
    without_output = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(user_id="user123", type=TaskOperation.OCR.value, status=TaskStatus.QUEUED.value),
    )

    assert with_output.output_encrypted is True
    assert without_output.output_encrypted is False


def test_update_task_flags_output_encrypted(task_table, encryption_provider):
    created = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(user_id="user123", type=TaskOperation.OCR.value, status=TaskStatus.QUEUED.value),
    )
    assert created.output_encrypted is False

    updated = task_table.update_task(
        task_id=created.id,
        form_data=TaskUpdateForm(status="completed", output=_sample_output()),
    )

    assert updated.output_encrypted is True


def test_encrypt_pending_output_backfills_legacy_rows(task_table, db_session, encryption_provider):
    legacy_task = task_module.Task(
        id="legacy-task-id",
        type=TaskOperation.OCR.value,
        status=TaskStatus.COMPLETED.value,
        user_id="user123",
        percentage=100.0,
        output=_sample_output().model_dump(),
        output_encrypted=False,
        created_at=0,
        updated_at=0,
    )
    db_session.add(legacy_task)
    db_session.commit()

    processed = task_table.encrypt_pending_output(batch_size=10)

    assert processed == 1

    stored_output = _raw_output(db_session, "legacy-task-id")
    assert stored_output["__enc__"] == "v1"

    fetched = task_table.get_task_by_id("legacy-task-id")
    assert fetched.output.text == SENSITIVE_TEXT
    assert fetched.output_encrypted is True

    # Idempotent : un second passage ne retrouve plus rien à faire.
    assert task_table.encrypt_pending_output(batch_size=10) == 0


def test_encrypt_pending_output_marks_tasks_without_output_as_done(task_table, encryption_provider):
    created = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(user_id="user123", type=TaskOperation.OCR.value, status=TaskStatus.QUEUED.value),
    )
    assert created.output_encrypted is False

    # Rien à chiffrer, mais la ligne est tout de même marquée pour ne plus être reprise.
    processed = task_table.encrypt_pending_output(batch_size=10)
    assert processed == 1
    assert task_table.get_task_by_id(created.id).output_encrypted is True

    assert task_table.encrypt_pending_output(batch_size=10) == 0


def test_encrypt_pending_output_respects_batch_size(task_table, db_session, encryption_provider):
    for i in range(3):
        db_session.add(
            task_module.Task(
                id=f"legacy-{i}",
                type=TaskOperation.OCR.value,
                status=TaskStatus.COMPLETED.value,
                user_id="user123",
                percentage=100.0,
                output=_sample_output().model_dump(),
                output_encrypted=False,
                created_at=0,
                updated_at=0,
            )
        )
    db_session.commit()

    first_batch = task_table.encrypt_pending_output(batch_size=2)
    second_batch = task_table.encrypt_pending_output(batch_size=2)

    assert first_batch == 2
    assert second_batch == 1
    assert task_table.encrypt_pending_output(batch_size=2) == 0


def test_task_without_output_never_touches_encryption_provider(task_table, monkeypatch):
    def _fail_if_called():
        raise AssertionError("encryption provider should not be constructed when output is absent")

    monkeypatch.setattr(task_module, "_get_encryption_provider", _fail_if_called)

    result = task_table.insert_new_task(
        user_id="user123",
        form_data=TaskForm(user_id="user123", type=TaskOperation.OCR.value, status=TaskStatus.QUEUED.value),
    )

    assert result.output is None
    assert task_table.get_task_by_id(result.id).output is None
