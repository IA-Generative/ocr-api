import pytest
from PIL import Image

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.connector.s3_connector import S3Connector
from services.base.worker import (
    FileNotSupported,
    AnyFileProcessWorker,
    hash_file,
    DefaultFileProcessWorker,
)
from src.schemas.input import InputForm
from src.schemas.task import TaskForm, TaskModel, TaskStatus, TaskOperation

from services.client.server import ServerClient
from src.schemas.output import OCRResult


server_client = ServerClient()


class MockeBaseModelPrediction(BaseModelPrediction):
    def __init__(self):
        super().__init__()

    def batch_predict(self, images: list, pages: list[Page], *args, **kwargs) -> list[Page]:
        return [Page(page=i) for i, _ in enumerate(images)]


@pytest.fixture
def dummy_task() -> TaskModel:
    task_dct = server_client.create_task(task_data=TaskForm(type="ocr", status="created").model_dump())
    return TaskModel(**task_dct)


@pytest.fixture
def mock_minio() -> S3Connector:
    return S3Connector()


@pytest.fixture
def mock_model() -> MockeBaseModelPrediction:
    return MockeBaseModelPrediction()


def test_get_content_file_success(mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel):
    expected_content = b"fake-bytes-content"
    tmp_path = "data.txt"
    with open(tmp_path, "wb") as f:
        f.write(expected_content)

    mock_minio.save(task_id=dummy_task.id, user_id=dummy_task.user_id, file_path=tmp_path)

    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    file_path = worker.get_content_file(task=dummy_task)
    with open(file_path, "rb") as f:
        content = f.read()

    assert content == expected_content
    mock_minio.delete_by_task_id(user_id=dummy_task.user_id, task_id=dummy_task.id)


def test_get_content_file_exception(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])

    with pytest.raises(Exception):
        worker.get_content_file(task=dummy_task)


def test_set_task_extras(mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel):
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    actual = worker.set_extras(task=dummy_task)
    assert actual.extras is not None


def test_transform_content_error_no_content_type(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="vvv/ssjpg",
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    dummy_task.extras = {}
    with open("tests/data/valid/identite.jpg", "rb") as f:
        expected_content = f.read()
        with pytest.raises(FileNotSupported):
            worker.transform_content(task=dummy_task, content=expected_content)


def test_transform_content_content_type_image(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )

    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    with open("tests/data/valid/identite.jpg", "rb") as f:
        actual = worker.transform_content(
            task=dummy_task,
            content=f,  # ty:ignore[invalid-argument-type]
        )
        assert isinstance(actual[0], Image.Image)


def test_transform_content_content_type_pdf(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/cerfa_13750-05-1.pdf",
        raw_filename="cerfa_13750-05-1.pdf",
        ext=".pdf",
        size=123456,
        content_type="application/pdf",  # Uncomment this line to simulate the absence of content_type
    )

    worker = AnyFileProcessWorker(
        name="test",
        file_connector=mock_minio,
        models=[mock_model],
    )

    actual = worker.transform_content(task=dummy_task, content=b"tests/data/valid/cerfa_13750-05-1.pdf")
    assert isinstance(actual[0], Image.Image)
    assert len(actual) == 1


def test_predict_on_pages(mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])

    image = Image.open("tests/data/valid/identite.jpg")
    actual = worker.predict_on_pages(task=dummy_task, pages=[image])
    assert actual is not None


def test_predict_get_from_hash(mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel):
    from services.base.cache import BaseCache

    input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )

    cache_task = TaskModel(
        id="1111",
        user_id="unk",
        type="",
        input=input,
        status=TaskStatus.COMPLETED.value,
        percentage=1,
        content_hash=hash_file(input.storage_file_path),
        output=OCRResult(
            type="mix",
            model_name="1",
            created_at=2,
            updated_at=3,
            version="1",
            total_pages=1,
            pages=[],
        ),
        created_at=0,
        updated_at=1,
    )

    class MockCache(BaseCache):
        def is_in_cache(self, task: TaskModel) -> bool:
            return True

        def get_task_from_cache(self, task: TaskModel) -> TaskModel:
            return cache_task

    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    mock_minio.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model], cache=MockCache())
    update_task = worker.process_task(task=dummy_task)
    assert update_task.percentage == cache_task.percentage
    assert update_task.status == TaskStatus.COMPLETED.value
    assert update_task.output == cache_task.output


def test_worker_predict_on_pages_raise_exception(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    class MockeExceptionWorker(AnyFileProcessWorker):
        def predict_on_pages(self, task: TaskModel, pages: list[Image.Image]) -> TaskModel:  # ty:ignore[invalid-method-override]
            raise Exception("Mocked exception")

    worker = MockeExceptionWorker(name="test", file_connector=mock_minio, models=[mock_model])
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    mock_minio.save(
        user_id=dummy_task.user_id,
        task_id=dummy_task.id,
        file_path=dummy_task.input.storage_file_path,
    )
    with pytest.raises(Exception):
        worker.process_task(task=dummy_task)


def test_raise_exception_on_retrieve_content(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    class MockeExceptionWorker(AnyFileProcessWorker):
        def get_content_file(self, task: TaskModel) -> str:
            raise Exception("Mocked exception")

    worker = MockeExceptionWorker(name="test", file_connector=mock_minio, models=[mock_model])
    with pytest.raises(Exception):
        worker.get_content_file(task=dummy_task)


def test_base_worker_is_applicable(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    assert worker.is_applicable(task=dummy_task) is True

    dummy_task.input.content_type = "image/jpg"
    assert worker.is_applicable(task=dummy_task) is True

    dummy_task.input.content_type = "application/pdf"
    assert worker.is_applicable(task=dummy_task) is True

    dummy_task.input.content_type = "text/plain"
    assert worker.is_applicable(task=dummy_task) is False


def test_base_worker_transform_content_no_input(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    dummy_task.input = None
    with pytest.raises(ValueError):
        worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
        worker.transform_content(task=dummy_task, content=b"fake-content")


def test_predict_on_pages_no_input_or_no_output(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    dummy_task.output = None
    with pytest.raises(ValueError):
        worker.predict_on_pages(task=dummy_task, pages=[])

    dummy_task.input = None

    with pytest.raises(ValueError):
        worker.predict_on_pages(task=dummy_task, pages=[])


def test__process_task_no_input(mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel):
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    dummy_task.input = None
    with pytest.raises(ValueError):
        worker._process_task(task=dummy_task)


def test__process_task_no_output(mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel):
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    dummy_task.output = None
    with pytest.raises(ValueError):
        worker._process_task(task=dummy_task)


def test__process_task(
    mock_minio: S3Connector,
    mock_model: MockeBaseModelPrediction,
    dummy_task: TaskModel,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        mock_minio,
        "get_by_task_id",
        lambda user_id, task_id: "tests/data/valid/identite.jpg",
    )
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    dummy_task.input = InputForm(
        storage_file_path="tests/data/valid/identite.jpg",
        raw_filename="identite.jpg",
        ext=".jpg",
        size=123456,
        content_type="image/jpg",  # Uncomment this line to simulate the absence of content_type
    )
    dummy_task.output = OCRResult(
        type="mix",
        model_name="1",
        created_at=2,
        updated_at=3,
        version="1",
        total_pages=1,
        pages=[],
    )

    actual = worker._process_task(task=dummy_task)
    assert actual is not None


def test_any_file_process_worker_set_extras(
    mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel
):
    worker = AnyFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    actual = worker.is_applicable(task=dummy_task)
    assert not actual

    dummy_task.input = None
    actual = worker.is_applicable(task=dummy_task)
    assert not actual


def test_default_file_processor(mock_minio: S3Connector, mock_model: MockeBaseModelPrediction, dummy_task: TaskModel):
    worker = DefaultFileProcessWorker(name="test", file_connector=mock_minio, models=[mock_model])
    actual = worker.is_applicable(task=dummy_task)
    assert not actual

    dummy_task.type = TaskOperation.DEFAULT.value
    actual = worker.is_applicable(task=dummy_task)
    assert actual
