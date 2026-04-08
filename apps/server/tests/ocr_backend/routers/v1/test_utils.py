import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Block the real S3 connector from connecting at import time
# ---------------------------------------------------------------------------
_mock_s3_connector = MagicMock()
_mock_connectors_module = MagicMock()
_mock_connectors_module.s3_client_connector = _mock_s3_connector
sys.modules.setdefault("ocr_backend.connectors", _mock_connectors_module)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_request(content: list[dict]) -> MagicMock:
    msg = MagicMock()
    msg.messages = [{"role": "user", "content": content}]
    return msg


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8  # minimal fake PNG


# ---------------------------------------------------------------------------
# retrieve_from_private_s3
# ---------------------------------------------------------------------------


def test_retrieve_from_s3_returns_tempfile(tmp_path):
    from ocr_backend.routers.v1.utils import retrieve_from_private_s3

    mock_s3 = MagicMock()
    mock_s3.client.get_object.return_value = {"Body": MagicMock(read=lambda: PNG_BYTES)}
    mock_s3.bucket_name = "my-bucket"

    with patch("ocr_backend.routers.v1.utils.s3_client_connector", mock_s3):
        path = retrieve_from_private_s3("docs/scan.png")

    assert isinstance(path, Path)
    assert path.exists()
    assert path.read_bytes() == PNG_BYTES
    assert path.suffix == ".png"
    path.unlink()


# ---------------------------------------------------------------------------
# retrieve_from_url
# ---------------------------------------------------------------------------


def test_retrieve_from_url_returns_tempfile():
    from ocr_backend.routers.v1.utils import retrieve_from_url

    mock_response = MagicMock()
    mock_response.content = PNG_BYTES
    mock_response.headers = {"Content-Type": "image/png"}
    mock_response.raise_for_status = MagicMock()

    with patch("ocr_backend.routers.v1.utils.requests.get", return_value=mock_response):
        path = retrieve_from_url("https://example.com/image.png")

    assert path.exists()
    assert path.read_bytes() == PNG_BYTES
    assert path.suffix == ".png"
    path.unlink()


def test_retrieve_from_url_rejects_unsupported_mime():
    from ocr_backend.routers.v1.utils import retrieve_from_url

    mock_response = MagicMock()
    mock_response.content = b"<html/>"
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.raise_for_status = MagicMock()

    with patch("ocr_backend.routers.v1.utils.requests.get", return_value=mock_response):
        with pytest.raises(ValueError, match="Unsupported MIME type"):
            retrieve_from_url("https://example.com/page.html")


# ---------------------------------------------------------------------------
# retrieve_file_or_image_from_message_content — image_url
# ---------------------------------------------------------------------------


def test_content_image_url_downloads_from_url():
    from ocr_backend.routers.v1.utils import retrieve_file_or_image_from_message_content

    mock_response = MagicMock()
    mock_response.content = PNG_BYTES
    mock_response.headers = {"Content-Type": "image/png"}
    mock_response.raise_for_status = MagicMock()

    content = [
        {"type": "text", "text": "OCR this"},
        {"type": "image_url", "image_url": {"url": "https://example.com/doc.png"}},
    ]

    with patch("ocr_backend.routers.v1.utils.requests.get", return_value=mock_response):
        path = retrieve_file_or_image_from_message_content(content)

    assert path.exists()
    path.unlink()


# ---------------------------------------------------------------------------
# retrieve_file_or_image_from_message_content — file with file_id (S3 key)
# ---------------------------------------------------------------------------


def test_content_file_id_downloads_from_s3():
    from ocr_backend.routers.v1.utils import retrieve_file_or_image_from_message_content

    mock_s3 = MagicMock()
    mock_s3.client.get_object.return_value = {"Body": MagicMock(read=lambda: PNG_BYTES)}
    mock_s3.bucket_name = "my-bucket"

    content = [
        {"type": "text", "text": "OCR this"},
        {"type": "file", "file": {"file_id": "uploads/scan.png"}},
    ]

    with patch("ocr_backend.routers.v1.utils.s3_client_connector", mock_s3):
        path = retrieve_file_or_image_from_message_content(content)

    assert path.exists()
    path.unlink()


# ---------------------------------------------------------------------------
# retrieve_file_or_image_from_message_content — file with file_data (http URL)
# ---------------------------------------------------------------------------


def test_content_file_data_http_url_downloads_from_url():
    from ocr_backend.routers.v1.utils import retrieve_file_or_image_from_message_content

    mock_response = MagicMock()
    mock_response.content = PNG_BYTES
    mock_response.headers = {"Content-Type": "image/png"}
    mock_response.raise_for_status = MagicMock()

    content = [
        {"type": "text", "text": "OCR this"},
        {"type": "file", "file": {"file_data": "https://example.com/doc.png"}},
    ]

    with patch("ocr_backend.routers.v1.utils.requests.get", return_value=mock_response):
        path = retrieve_file_or_image_from_message_content(content)

    assert path.exists()
    path.unlink()


# ---------------------------------------------------------------------------
# retrieve_file_or_image_from_message_content — file with file_data (S3 key)
# ---------------------------------------------------------------------------


def test_content_file_data_s3_key_downloads_from_s3():
    from ocr_backend.routers.v1.utils import retrieve_file_or_image_from_message_content

    mock_s3 = MagicMock()
    mock_s3.client.get_object.return_value = {"Body": MagicMock(read=lambda: PNG_BYTES)}
    mock_s3.bucket_name = "my-bucket"

    content = [
        {"type": "text", "text": "OCR this"},
        {"type": "file", "file": {"file_data": "private/archive.pdf"}},
    ]

    with patch("ocr_backend.routers.v1.utils.s3_client_connector", mock_s3):
        path = retrieve_file_or_image_from_message_content(content)

    assert path.exists()
    path.unlink()


# ---------------------------------------------------------------------------
# retrieve_file_or_image_from_message_content — no valid part
# ---------------------------------------------------------------------------


def test_content_no_valid_part_raises():
    from ocr_backend.routers.v1.utils import retrieve_file_or_image_from_message_content

    content = [{"type": "text", "text": "just text, no image"}]

    with pytest.raises(ValueError, match="No valid image URL or file data"):
        retrieve_file_or_image_from_message_content(content)
