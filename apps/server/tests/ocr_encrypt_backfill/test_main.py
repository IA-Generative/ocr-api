from contextlib import contextmanager

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import ocr_encrypt_backfill.main as backfill_main
import src.schemas.task as task_module
from src.connector.encryption.local_provider import LocalEncryptionProvider
from src.schemas import Base
from src.schemas.output import OCRResult, Page
from src.schemas.task import Task, TaskOperation, TaskStatus, TaskTable

SENSITIVE_TEXT = "secret backfill content"


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def task_table(db_session, monkeypatch) -> TaskTable:
    @contextmanager
    def fake_get_db():
        yield db_session

    table = TaskTable(get_db=fake_get_db)
    monkeypatch.setattr(backfill_main, "task_table", table)
    return table


@pytest.fixture
def encryption_provider(monkeypatch):
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


def _insert_legacy_task(db_session, task_id: str) -> None:
    db_session.add(
        Task(
            id=task_id,
            type=TaskOperation.OCR.value,
            status=TaskStatus.COMPLETED.value,
            user_id="user-backfill",
            percentage=100.0,
            output=_sample_output().model_dump(),
            output_encrypted=False,
            created_at=0,
            updated_at=0,
        )
    )
    db_session.commit()


def test_main_encrypts_legacy_rows(task_table, db_session, encryption_provider):
    _insert_legacy_task(db_session, "legacy-backfill-1")

    total = backfill_main.main(batch_size=50)

    assert total == 1
    fetched = task_table.get_task_by_id("legacy-backfill-1")
    assert fetched.output.text == SENSITIVE_TEXT
    assert fetched.output_encrypted is True


def test_main_is_idempotent(task_table, db_session, encryption_provider):
    _insert_legacy_task(db_session, "legacy-backfill-2")

    backfill_main.main(batch_size=50)
    second_run_total = backfill_main.main(batch_size=50)

    assert second_run_total == 0
    fetched = task_table.get_task_by_id("legacy-backfill-2")
    assert fetched.output.text == SENSITIVE_TEXT


def test_main_paginates_across_multiple_batches(task_table, db_session, encryption_provider):
    for i in range(5):
        _insert_legacy_task(db_session, f"legacy-backfill-batch-{i}")

    total = backfill_main.main(batch_size=2)

    assert total == 5
    for i in range(5):
        fetched = task_table.get_task_by_id(f"legacy-backfill-batch-{i}")
        assert fetched.output.text == SENSITIVE_TEXT
        assert fetched.output_encrypted is True
