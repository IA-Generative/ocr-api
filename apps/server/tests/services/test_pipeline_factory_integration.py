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
        "save",
        lambda *args, **kwargs: dummy_task_image_default.input.raw_filename,
    )

    worker = load_worker("test_worker", 2, 0.5)
    task = worker.process(task=dummy_task_image_default)
    assert len(task.output.pages) != 0
    assert len(task.output.pages[0].form_entries) == 0


@pytest.fixture(scope="function")
def dummy_task_pdf_form_ocr(task_table: TaskTable) -> TaskModel:
    return task_table.insert_new_task(
        user_id="123",
        form_data=TaskForm(
            user_id="123",
            type=TaskOperation.OCR.value,
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


def test_load_factory_with_pdf_form_worker(
    monkeypatch: pytest.MonkeyPatch,
    dummy_task_pdf_form_ocr: TaskModel,
    task_table: TaskTable,
):
    from business.llm.models.template import FormFieldExtractor
    from src.schemas.template import LLMFormField

    monkeypatch.setattr(
        "business.forms.workers.pdf_worker.task_table.update_task",
        task_table.update_task,
    )

    monkeypatch.setattr(
        s3_client_connector,
        "get_by_task_id",
        lambda *args, **kwargs: dummy_task_pdf_form_ocr.input.raw_filename,
    )
    monkeypatch.setattr(
        s3_client_connector,
        "save",
        lambda *args, **kwargs: dummy_task_pdf_form_ocr.input.raw_filename,
    )

    def fake_create(*args, **kwargs):
        return [
            LLMFormField(
                name="dummy_name",
                value="dummy_value",
                type="text",
                sections=[],
                filled=False,
            )
        ]

    async def fake_create_async(*args, **kwargs):
        return fake_create(*args, **kwargs)

    original_init = FormFieldExtractor.__init__

    def patched_init(self, client, model_name):
        original_init(self, client, model_name)
        # Patch sync
        # self.instructor.chat.completions.create = fake_create
        # Patch async
        self.instructor.chat.completions.create = fake_create_async

    monkeypatch.setattr(FormFieldExtractor, "__init__", patched_init)

    worker = load_worker("test_worker", 2, 0.5)
    task = worker.process(task=dummy_task_pdf_form_ocr)
    assert len(task.output.pages) != 0
    assert len(task.output.pages[1].form_entries) != 0


@pytest.fixture(scope="function")
def dummy_task_image_form_vlm(task_table: TaskTable) -> TaskModel:
    return task_table.insert_new_task(
        user_id="123",
        form_data=TaskForm(
            user_id="123",
            type=TaskOperation.VLM_OCR.value,
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


def test_load_factory_with_image_form_worker_with_vlm(
    monkeypatch: pytest.MonkeyPatch,
    dummy_task_image_form_vlm: TaskModel,
    task_table: TaskTable,
):
    ############### MOCKING ###############
    from business.llm.models.classification import FormClassification
    from src.schemas.template import ImageFormDetector

    monkeypatch.setattr(
        "services.base.worker.task_table.update_task",
        task_table.update_task,
    )

    monkeypatch.setattr(
        s3_client_connector,
        "get_by_task_id",
        lambda *args, **kwargs: dummy_task_image_form_vlm.input.raw_filename,
    )
    monkeypatch.setattr(
        s3_client_connector,
        "save",
        lambda *args, **kwargs: dummy_task_image_form_vlm.input.raw_filename,
    )

    def fake_create(*args, **kwargs):
        return ImageFormDetector(is_form=True, confidence=0.95)

    async def fake_create_async(*args, **kwargs):
        return fake_create(*args, **kwargs)

    original_init = FormClassification.__init__

    def patched_init(self: FormClassification, client, model_name):
        original_init(self, client, model_name)
        # Patch sync
        # self.instructor.chat.completions.create = fake_create
        # Patch async
        self.client.chat.completions.create = fake_create_async

    monkeypatch.setattr(FormClassification, "__init__", patched_init)

    ##### LLMToForm ####

    from business.llm.models.vision import LLMToForm
    from src.schemas.template import LLMFormField

    def form_fake_create(*args, **kwargs):
        return [
            LLMFormField(
                name="dummy_key",
                value="dummy_value",
                type="checkbox",
                sections=[],
                filled=False,
            )
        ]

    async def form_fake_create_async(*args, **kwargs):
        return form_fake_create(*args, **kwargs)

    form_original_init = LLMToForm.__init__

    def form_patched_init(self, client, model_name):
        form_original_init(self, client, model_name)
        # Patch sync
        # self.instructor.chat.completions.create = fake_create
        # Patch async
        self.client.chat.completions.create = form_fake_create_async

    monkeypatch.setattr(LLMToForm, "__init__", form_patched_init)

    ##### VisionOCR ####

    from business.llm.models.base import VisionLLMOCR

    def vision_fake_create(*args, **kwargs):
        class Message:
            def __init__(self, content):
                self.content = content

            def strip(self):
                return self.content.strip()

        class Choice:
            def __init__(self, content):
                self.message = Message(content)

        class Response:
            def __init__(self, content):
                self.choices = [Choice(content)]

        return Response("mock text")

    async def vision_fake_create_async(*args, **kwargs):
        return vision_fake_create(*args, **kwargs)

    vision_original_init = VisionLLMOCR.__init__

    def form_patched_init(self, client, model_name):
        vision_original_init(self, client, model_name)
        # Patch sync
        # self.instructor.chat.completions.create = fake_create
        # Patch async
        self.client.chat.completions.create = vision_fake_create_async

    monkeypatch.setattr(VisionLLMOCR, "__init__", form_patched_init)
    ############################################################

    worker = load_worker("test_worker", 2, 0.5)
    task = worker.process(task=dummy_task_image_form_vlm)
    assert len(task.output.pages) != 0
    assert len(task.output.pages[0].form_entries) != 0
