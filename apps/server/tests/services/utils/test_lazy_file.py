from io import BytesIO

import pytest
from PIL import Image

from services.utils.lazy_file import LazyFileImageList

ODT_PATH = "tests/data/file-sample_100kB.odt"
DOCX_PATH = "tests/data/valid/file-sample_500kB.docx"


def test_bytes_to_image_converts_to_rgb():
    lazy = LazyFileImageList.__new__(LazyFileImageList)

    grayscale = Image.new("L", (10, 10))
    buffer = BytesIO()
    grayscale.save(buffer, format="PNG")

    image = lazy.bytes_to_image(buffer.getvalue())

    assert isinstance(image, Image.Image)
    assert image.mode == "RGB"


def test_lazy_file_image_list_len_and_indexing():
    lazy = LazyFileImageList(ODT_PATH)

    assert len(lazy) == len(lazy.info.pages)
    assert len(lazy) > 0

    first_page = lazy[0]
    assert isinstance(first_page, Image.Image)
    assert first_page.mode == "RGB"


def test_lazy_file_image_list_negative_index():
    lazy = LazyFileImageList(ODT_PATH)

    assert lazy[-1].size == lazy[len(lazy) - 1].size


def test_lazy_file_image_list_slice_returns_list():
    lazy = LazyFileImageList(ODT_PATH)

    pages = lazy[0 : len(lazy)]
    assert isinstance(pages, list)
    assert len(pages) == len(lazy)
    assert all(isinstance(page, Image.Image) for page in pages)


def test_lazy_file_image_list_index_out_of_range():
    lazy = LazyFileImageList(ODT_PATH)

    with pytest.raises(IndexError):
        lazy[len(lazy)]


def test_lazy_file_image_list_invalid_index_type():
    lazy = LazyFileImageList(ODT_PATH)

    with pytest.raises(TypeError):
        lazy["0"]


def test_lazy_file_image_list_docx():
    lazy = LazyFileImageList(DOCX_PATH)

    assert len(lazy) > 0
    assert isinstance(lazy[0], Image.Image)


def test_lazy_file_image_list_repr():
    lazy = LazyFileImageList(ODT_PATH)

    assert repr(lazy) == f"<LazyPdfImageList pages={len(lazy)} path='{ODT_PATH}'>"
