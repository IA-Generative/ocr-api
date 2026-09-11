import pytest

from business.liteparse.worker.liteparse_worker import LiteparseWorker
from business.liteparse.models.liteparse_model import LITEPARSE_CONTENT_TYPES
from src.schemas.input import InputForm
from src.schemas.output import Page
from src.schemas.task import TaskForm, TaskModel, TaskOperation, task_table
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_task(content_type: str, filename: str, task_type: TaskOperation = TaskOperation.DEFAULT) -> TaskModel:
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


@pytest.mark.parametrize("op", [TaskOperation.VLM_OCR, TaskOperation.DOCLING, TaskOperation.FORMS])
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


# ===========================================================================
# predict_on_pages — regression: a single uploaded file expands into N real
# document pages/slides via LiteparseExtractionModel.batch_predict. The base
# BaseWorker.predict_on_pages/_predict_on_ocr_batch only ever kept page 0 of
# that expansion (1 input item -> 1 output page), silently dropping every
# other page for a multi-page DOCX/PPTX/etc.
# ===========================================================================


def _multi_page_model(pages_to_return: list[Page]):
    """A fake model whose batch_predict ignores the (single-item) input batch
    and returns `pages_to_return`, exactly like LiteparseExtractionModel does
    for a real multi-page/multi-slide document."""
    model = MagicMock()
    model.batch_predict.return_value = pages_to_return
    return model


def test_predict_on_pages_keeps_every_page_from_a_multi_page_document(worker):
    task = _make_task(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "doc.docx",
    )
    expected_pages = [Page(page=i, boxes=[]) for i in range(1, 6)]  # 5-page document
    worker.models = [_multi_page_model(expected_pages)]

    result = worker.predict_on_pages(task, pages=[b"fake docx bytes"])

    assert result.output.total_pages == 5
    assert result.output.pages == expected_pages


def test_predict_on_pages_single_page_document_still_works(worker):
    task = _make_task("text/csv", "data.csv")
    expected_pages = [Page(page=1, boxes=[])]
    worker.models = [_multi_page_model(expected_pages)]

    result = worker.predict_on_pages(task, pages=[b"col1,col2\n1,2"])

    assert result.output.total_pages == 1
    assert result.output.pages == expected_pages


def test_predict_on_pages_empty_model_result_does_not_crash(worker):
    """No pages parsed (e.g. an empty file) must not divide by zero in the
    percentage checkpoint - total_pages ends up 0, not left at the file count."""
    task = _make_task("text/csv", "data.csv")
    worker.models = [_multi_page_model([])]

    result = worker.predict_on_pages(task, pages=[b""])

    assert result.output.total_pages == 0
    assert result.output.pages == []


def test_predict_on_pages_chains_multiple_models(worker):
    """Each model in `self.models` receives the previous model's `pages` output,
    same contract as BaseWorker._predict_on_ocr_batch."""
    task = _make_task(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "doc.docx",
    )
    first_pass = [Page(page=1, boxes=[]), Page(page=2, boxes=[])]
    second_pass = [Page(page=1, boxes=[]), Page(page=2, boxes=[])]
    model_a = _multi_page_model(first_pass)
    model_b = _multi_page_model(second_pass)
    worker.models = [model_a, model_b]

    result = worker.predict_on_pages(task, pages=[b"fake docx bytes"])

    model_b.batch_predict.assert_called_once_with(images=[b"fake docx bytes"], pages=first_pass)
    assert result.output.pages == second_pass
