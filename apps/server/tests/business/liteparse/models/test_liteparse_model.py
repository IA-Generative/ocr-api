from unittest.mock import MagicMock, patch

import pytest

from business.liteparse.models.liteparse_model import (
    LITEPARSE_CONTENT_TYPES,
    LiteparseExtractionModel,
    _CONTENT_TYPE_TO_EXT,
)
from src.schemas.input import InputForm
from src.schemas.task import TaskForm, TaskModel, TaskOperation, task_table

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_task(content_type: str, filename: str, ext: str = "") -> TaskModel:
    task = task_table.insert_new_task(
        user_id="test-user",
        form_data=TaskForm(user_id="test-user", type=TaskOperation.DEFAULT, status="created"),
    )
    task.input = InputForm(
        storage_file_path=f"test-user/{task.id}/{filename}",
        raw_filename=filename,
        content_type=content_type,
        ext=ext or ("." + filename.rsplit(".", 1)[-1] if "." in filename else ""),
        size=1024,
    )
    return task


def _make_text_item(text: str, x: float, y: float, w: float, h: float, confidence: float = 0.95):
    item = MagicMock()
    item.text = text
    item.x = x
    item.y = y
    item.width = w
    item.height = h
    item.confidence = confidence
    return item


def _make_lp_page(page_num: int, width: float, height: float, text_items=None, markdown: str = ""):
    page = MagicMock()
    page.page_num = page_num
    page.width = width
    page.height = height
    page.text_items = text_items or []
    page.markdown = markdown
    return page


def _make_parse_result(pages=None, text: str = ""):
    result = MagicMock()
    result.pages = pages or []
    result.text = text
    return result


def _make_screenshot(page_num: int):
    s = MagicMock()
    s.page_num = page_num
    s.image_bytes = b"PNG_BYTES"
    return s


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def model_no_s3():
    with patch("business.liteparse.models.liteparse_model.LiteParse") as mock_cls:
        mock_cls.return_value = MagicMock()
        m = LiteparseExtractionModel(file_connector=None)
        m._parser = mock_cls.return_value
        yield m


@pytest.fixture
def mock_s3():
    connector = MagicMock()
    connector.bucket_name = "test-bucket"
    connector.client = MagicMock()
    connector.client.generate_presigned_url.return_value = "https://s3/presigned"
    return connector


@pytest.fixture
def model_with_s3(mock_s3):
    with patch("business.liteparse.models.liteparse_model.LiteParse") as mock_cls:
        mock_cls.return_value = MagicMock()
        m = LiteparseExtractionModel(file_connector=mock_s3)
        m._parser = mock_cls.return_value
        yield m


# ===========================================================================
# is_applicable
# ===========================================================================


@pytest.mark.parametrize(
    "content_type",
    [
        "text/csv",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        "application/msword",
        "text/rtf",
        "application/vnd.apple.pages",
        "application/vnd.apple.numbers",
        "application/vnd.apple.keynote",
    ],
)
def test_is_applicable_true(model_no_s3, content_type):
    task = _make_task(content_type, "file.docx")
    assert model_no_s3.is_applicable(task) is True


@pytest.mark.parametrize(
    "content_type",
    [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "application/octet-stream",
        "text/html",
    ],
)
def test_is_applicable_false(model_no_s3, content_type):
    task = _make_task(content_type, "file.bin")
    assert model_no_s3.is_applicable(task) is False


def test_all_listed_types_are_in_ext_map():
    """Every MIME type must map to a file extension so temp files are named correctly."""
    missing = [ct for ct in LITEPARSE_CONTENT_TYPES if ct not in _CONTENT_TYPE_TO_EXT]
    assert missing == [], f"Missing extension mapping for: {missing}"


# ===========================================================================
# _resolve_extension
# ===========================================================================


def test_resolve_extension_from_ext_field(model_no_s3):
    task = _make_task(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "doc.docx",
        ext=".docx",
    )
    assert model_no_s3._resolve_extension(task) == ".docx"


def test_resolve_extension_from_filename(model_no_s3):
    task = _make_task("text/csv", "data.csv", ext="")
    task.input.ext = ""
    assert model_no_s3._resolve_extension(task) == ".csv"


def test_resolve_extension_fallback_to_mime(model_no_s3):
    task = _make_task("application/vnd.oasis.opendocument.text", "file", ext="")
    task.input.ext = ""
    task.input.raw_filename = "file"
    assert model_no_s3._resolve_extension(task) == ".odt"


# ===========================================================================
# batch_predict — bboxes
# ===========================================================================


def test_batch_predict_returns_one_page_per_lp_page(model_no_s3):
    task = _make_task("text/csv", "data.csv")
    model_no_s3.set_current_task(task)

    lp_pages = [
        _make_lp_page(1, 612, 792, [_make_text_item("Hello", 10, 20, 100, 15)]),
        _make_lp_page(2, 612, 792, [_make_text_item("World", 10, 20, 80, 15)]),
    ]
    model_no_s3._parser.parse.return_value = _make_parse_result(pages=lp_pages)
    model_no_s3._parser.screenshot.return_value = []

    result = model_no_s3.batch_predict(images=[b"raw"])

    assert len(result) == 2
    assert result[0].page == 1
    assert result[1].page == 2


def test_batch_predict_bbox_normalization(model_no_s3):
    task = _make_task("text/csv", "data.csv")
    model_no_s3.set_current_task(task)

    item = _make_text_item("Test", x=61.2, y=79.2, w=122.4, h=39.6, confidence=0.9)
    lp_pages = [_make_lp_page(1, width=612.0, height=792.0, text_items=[item])]
    model_no_s3._parser.parse.return_value = _make_parse_result(pages=lp_pages)
    model_no_s3._parser.screenshot.return_value = []

    result = model_no_s3.batch_predict(images=[b"raw"])

    bbox = result[0].boxes[0]
    assert pytest.approx(bbox.x, abs=1e-4) == 0.1
    assert pytest.approx(bbox.y, abs=1e-4) == 0.1
    assert pytest.approx(bbox.width, abs=1e-4) == 0.2
    assert pytest.approx(bbox.height, abs=1e-4) == 0.05
    assert pytest.approx(bbox.confidence, abs=1e-4) == 0.9
    assert bbox.text == "Test"


def test_batch_predict_confidence_defaults_to_1_when_none(model_no_s3):
    task = _make_task("text/csv", "data.csv")
    model_no_s3.set_current_task(task)

    item = _make_text_item("X", 0, 0, 10, 10, confidence=None)
    item.confidence = None
    lp_pages = [_make_lp_page(1, 100, 100, [item])]
    model_no_s3._parser.parse.return_value = _make_parse_result(pages=lp_pages)
    model_no_s3._parser.screenshot.return_value = []

    result = model_no_s3.batch_predict(images=[b"raw"])
    assert result[0].boxes[0].confidence == 1.0


def test_batch_predict_empty_text_items_filtered(model_no_s3):
    task = _make_task("text/csv", "data.csv")
    model_no_s3.set_current_task(task)

    items = [
        _make_text_item("  ", 0, 0, 10, 10),  # whitespace only — must be filtered
        _make_text_item("Hello", 10, 10, 50, 15),
    ]
    lp_pages = [_make_lp_page(1, 100, 100, items)]
    model_no_s3._parser.parse.return_value = _make_parse_result(pages=lp_pages)
    model_no_s3._parser.screenshot.return_value = []

    result = model_no_s3.batch_predict(images=[b"raw"])
    assert len(result[0].boxes) == 1
    assert result[0].boxes[0].text == "Hello"


def test_batch_predict_fallback_markdown_when_no_text_items(model_no_s3):
    task = _make_task("text/csv", "data.csv")
    model_no_s3.set_current_task(task)

    lp_pages = [_make_lp_page(1, 612, 792, text_items=[], markdown="# Title\n\nSome text")]
    model_no_s3._parser.parse.return_value = _make_parse_result(pages=lp_pages)
    model_no_s3._parser.screenshot.return_value = []

    result = model_no_s3.batch_predict(images=[b"raw"])
    assert len(result[0].boxes) == 1
    assert result[0].boxes[0].text == "# Title\n\nSome text"
    assert result[0].boxes[0].x == 0
    assert result[0].boxes[0].width == 1


def test_batch_predict_fallback_full_text_when_no_pages(model_no_s3):
    task = _make_task("text/csv", "data.csv")
    model_no_s3.set_current_task(task)

    model_no_s3._parser.parse.return_value = _make_parse_result(pages=[], text="Fallback text")
    model_no_s3._parser.screenshot.return_value = []

    result = model_no_s3.batch_predict(images=[b"raw"])
    assert len(result) == 1
    assert result[0].page == 1
    assert result[0].boxes[0].text == "Fallback text"


def test_batch_predict_parse_error_returns_empty_page(model_no_s3):
    task = _make_task("text/csv", "data.csv")
    model_no_s3.set_current_task(task)

    model_no_s3._parser.parse.side_effect = RuntimeError("parse failed")

    result = model_no_s3.batch_predict(images=[b"raw"])
    assert len(result) == 1
    assert result[0].boxes == []


# ===========================================================================
# batch_predict — screenshots
# ===========================================================================


def test_batch_predict_screenshots_uploaded_per_page(model_with_s3, mock_s3):
    task = _make_task("text/csv", "data.csv")
    model_with_s3.set_current_task(task)

    lp_pages = [
        _make_lp_page(1, 612, 792, [_make_text_item("A", 0, 0, 10, 10)]),
        _make_lp_page(2, 612, 792, [_make_text_item("B", 0, 0, 10, 10)]),
    ]
    model_with_s3._parser.parse.return_value = _make_parse_result(pages=lp_pages)
    model_with_s3._parser.screenshot.return_value = [
        _make_screenshot(1),
        _make_screenshot(2),
    ]

    result = model_with_s3.batch_predict(images=[b"raw"])

    assert mock_s3.client.upload_fileobj.call_count == 2
    # La presigned URL n'est plus générée à l'upload : seule la clé S3 est stockée,
    # l'URL est générée à la demande via la route /tasks/{id}/page/{n}.
    assert mock_s3.client.generate_presigned_url.call_count == 0

    # Each page has a page_url pointing to its S3 key
    assert result[0].page_url == f"{task.user_id}/{task.id}/images/page_1.png"
    assert result[1].page_url == f"{task.user_id}/{task.id}/images/page_2.png"


def test_batch_predict_screenshot_key_format(model_with_s3, mock_s3):
    task = _make_task("text/csv", "data.csv")
    model_with_s3.set_current_task(task)

    lp_pages = [_make_lp_page(1, 612, 792, [_make_text_item("A", 0, 0, 10, 10)])]
    model_with_s3._parser.parse.return_value = _make_parse_result(pages=lp_pages)
    model_with_s3._parser.screenshot.return_value = [_make_screenshot(1)]

    result = model_with_s3.batch_predict(images=[b"raw"])

    expected_key = f"{task.user_id}/{task.id}/images/page_1.png"
    assert result[0].page_url == expected_key


def test_batch_predict_screenshot_failure_does_not_raise(model_with_s3, mock_s3):
    task = _make_task("text/csv", "data.csv")
    model_with_s3.set_current_task(task)

    lp_pages = [_make_lp_page(1, 612, 792, [_make_text_item("A", 0, 0, 10, 10)])]
    model_with_s3._parser.parse.return_value = _make_parse_result(pages=lp_pages)
    model_with_s3._parser.screenshot.side_effect = RuntimeError("screenshot boom")

    result = model_with_s3.batch_predict(images=[b"raw"])

    # Text extraction still succeeds
    assert len(result) == 1
    assert result[0].page_url is None


def test_batch_predict_no_s3_no_page_url(model_no_s3):
    task = _make_task("text/csv", "data.csv")
    model_no_s3.set_current_task(task)

    lp_pages = [_make_lp_page(1, 612, 792, [_make_text_item("Hi", 0, 0, 10, 10)])]
    model_no_s3._parser.parse.return_value = _make_parse_result(pages=lp_pages)
    model_no_s3._parser.screenshot.return_value = []

    result = model_no_s3.batch_predict(images=[b"raw"])
    assert result[0].page_url is None
