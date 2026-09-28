import pytest

from src.schemas.task import (
    TaskTable,
    TaskForm,
    TaskModel,
    TaskOperation,
)
from src.schemas.templates import TemplateTable
from src.schemas.input import InputForm
from services.factory import load_worker, s3_client_connector


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from src.schemas import Base


@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture(scope="module")
def task_table(db_session) -> TaskTable:
    @contextmanager
    def fake_get_db():
        yield db_session

    return TaskTable(get_db=fake_get_db)


@pytest.fixture(scope="module")
def template_table(db_session) -> TemplateTable:
    @contextmanager
    def fake_get_db():
        yield db_session

    return TemplateTable(get_db=fake_get_db)


@pytest.fixture(scope="function")
def dummy_task_pdf_form(task_table: TaskTable) -> TaskModel:
    return task_table.insert_new_task(
        user_id="123",
        form_data=TaskForm(
            user_id="123",
            type=TaskOperation.DEFAULT.value,
            status="created",
            group_id="DEFAULT",
            input=InputForm(
                storage_file_path="s3://bucket/path/to/file",
                raw_filename="tests/data/valid/cerfa_11573-09-filled.pdf",
                size=1024,
                content_type="application/pdf",
                ext="pdf",
            ),
        ),
    )


def test_load_factory_default_pdf_worker_with_pdf_form_worker(
    monkeypatch: pytest.MonkeyPatch,
    dummy_task_pdf_form: TaskModel,
    task_table: TaskTable,
):
    monkeypatch.setattr(
        "business.forms.workers.pdf_worker.task_table.update_task",
        task_table.update_task,
    )
    monkeypatch.setattr(
        s3_client_connector,
        "get_by_task_id",
        lambda *args, **kwargs: dummy_task_pdf_form.input.raw_filename,
    )
    monkeypatch.setattr(
        s3_client_connector,
        "download_by_s3_key",
        lambda *args, **kwargs: dummy_task_pdf_form.input.raw_filename,
    )
    monkeypatch.setattr(
        s3_client_connector,
        "save",
        lambda *args, **kwargs: dummy_task_pdf_form.input.raw_filename,
    )

    worker = load_worker("test_worker", 2, 0.5)
    task = worker.process(task=dummy_task_pdf_form)
    assert len(task.output.pages) != 0
    assert len(task.output.pages[1].form_entries) != 0


@pytest.fixture(scope="function")
def dummy_task_image_default(task_table: TaskTable) -> TaskModel:
    return task_table.insert_new_task(
        user_id="123",
        form_data=TaskForm(
            user_id="123",
            type=TaskOperation.DEFAULT.value,
            status="created",
            group_id="DEFAULT",
            input=InputForm(
                storage_file_path="s3://bucket/path/to/file",
                raw_filename="tests/data/valid/formulaire-cerfa-complete.png",
                size=1024,
                content_type="image/png",
                ext="png",
            ),
        ),
    )


def test_load_factory_default_worker_with_image(
    monkeypatch: pytest.MonkeyPatch,
    dummy_task_image_default: TaskModel,
    task_table: TaskTable,
):
    monkeypatch.setattr(
        "business.forms.workers.pdf_worker.task_table.update_task",
        task_table.update_task,
    )
    monkeypatch.setattr(
        s3_client_connector,
        "get_by_task_id",
        lambda *args, **kwargs: dummy_task_image_default.input.raw_filename,
    )
    monkeypatch.setattr(
        s3_client_connector,
        "download_by_s3_key",
        lambda *args, **kwargs: dummy_task_image_default.input.raw_filename,
    )
    monkeypatch.setattr(
        s3_client_connector,
        "save",
        lambda *args, **kwargs: dummy_task_image_default.input.raw_filename,
    )

    worker = load_worker("test_worker", 2, 0.5)
    task = worker.process(task=dummy_task_image_default)
    assert len(task.output.pages) != 0
    assert len(task.output.pages[0].form_entries) == 0
