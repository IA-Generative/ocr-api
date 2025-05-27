import PIL.Image
import pytest
import PIL
from ocr_service.utils.lazy_pdf import LazyPdfImageList


def test_lazy_load_pdf():
    pages = LazyPdfImageList("tests/data/valid/cerfa_13750-05-1.pdf")
    assert len(pages) == 1
    assert len(pages) >= 1

    assert isinstance(pages[0], PIL.Image.Image)
    assert isinstance(pages[-1], PIL.Image.Image)

    with pytest.raises(IndexError):
        pages[200000]

    with pytest.raises(TypeError):
        pages["1"]
