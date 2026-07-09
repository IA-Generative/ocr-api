import pytest

from business.liteparse.worker.liteparse_worker import LiteparseWorker
from business.liteparse.models.liteparse_model import LITEPARSE_CONTENT_TYPES
from src.schemas.input import InputForm
from src.schemas.task import TaskForm, TaskModel, TaskOperation, task_table
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_task(
    content_type: str, filename: str, task_type: TaskOperation = TaskOperation.DEFAULT
) -> TaskModel:
    task = task_table.insert_new_task(
        user_id="test-user",
        form_data=TaskForm(user_id="test-user", type=task_type, status="created"),
    )
    _, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
    task.input = InputForm(
        storage_file_path=f"test-user/{task.id}/{filename}",
        raw_filename=filename,
        content_type=content_type,
        ext=f".{ext}" if ext else "",
        size=1024,
    )
    return task


@pytest.fixture
def worker():
    connector = MagicMock()
    connector.bucket_name = "test-bucket"
    return LiteparseWorker(
        name="liteparse-worker",
        file_connector=connector,
        models=[],
        batch_size=1,
        worker_weight=1,
        cache=None,
    )


# ===========================================================================
# is_applicable
# ===========================================================================


@pytest.mark.parametrize(
    "content_type,filename",
    [
        ("text/csv", "data.csv"),
        (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "doc.docx",
        ),
        (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "sheet.xlsx",
        ),
        (
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "pres.pptx",
        ),
        ("application/vnd.oasis.opendocument.text", "doc.odt"),
        ("application/vnd.oasis.opendocument.spreadsheet", "sheet.ods"),
        ("application/vnd.oasis.opendocument.presentation", "pres.odp"),
        ("text/rtf", "doc.rtf"),
        ("application/msword", "doc.doc"),
    ],
)
def test_is_applicable_true(worker, content_type, filename):
    task = _make_task(content_type, filename)
    assert worker.is_applicable(task) is True


@pytest.mark.parametrize(
    "content_type,filename",
    [
        ("application/pdf", "doc.pdf"),
        ("image/jpeg", "photo.jpg"),
        ("image/png", "image.png"),
        ("application/octet-stream", "file.bin"),
    ],
)
def test_is_applicable_false_wrong_mime(worker, content_type, filename):
    task = _make_task(content_type, filename)
    assert worker.is_applicable(task) is False


@pytest.mark.parametrize(
    "op", [TaskOperation.VLM_OCR, TaskOperation.DOCLING, TaskOperation.FORMS]
)
def test_is_applicable_false_wrong_operation(worker, op):
    task = _make_task("text/csv", "data.csv", task_type=op)
    assert worker.is_applicable(task) is False


# ===========================================================================
# transform_content
# ===========================================================================


def test_transform_content_bytes_passthrough(worker):
    task = _make_task("text/csv", "data.csv")
    raw = b"col1,col2\n1,2"
    result = worker.transform_content(task, raw)
    assert result == [raw]


def test_transform_content_file_path_reads_file(worker, tmp_path):
    task = _make_task("text/csv", "data.csv")
    f = tmp_path / "data.csv"
    f.write_bytes(b"col1,col2\n1,2")
    result = worker.transform_content(task, str(f))
    assert result == [b"col1,col2\n1,2"]


def test_transform_content_returns_list(worker):
    task = _make_task("text/csv", "data.csv")
    result = worker.transform_content(task, b"data")
    assert isinstance(result, list)
    assert len(result) == 1


# ===========================================================================
# initialization
# ===========================================================================


def test_worker_initialization(worker):
    assert worker.name == "liteparse-worker"
    assert worker.batch_size == 1
    assert worker.worker_weight == 1


def test_all_liteparse_types_trigger_worker(worker):
    """Every declared MIME type must make is_applicable return True with DEFAULT operation."""
    for mime in LITEPARSE_CONTENT_TYPES:
        task = _make_task(mime, "file.bin")
        assert worker.is_applicable(task) is True, f"Expected True for {mime}"
