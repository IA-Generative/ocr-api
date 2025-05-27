from io import BytesIO
from pathlib import Path

from PIL import Image

from src.schemas.output import MarkdownPageWithBBox


def test_predict():
    from ocr_service.models.docling_ocr import DoclingInferOCR

    image = Image.open("tests/data/valid/formulaire-cerfa-complete.png")

    obj = DoclingInferOCR()

    list_md_page: list[MarkdownPageWithBBox] = obj.batch_predict([image])

    assert len(list_md_page)
    assert all(isinstance(md_page, MarkdownPageWithBBox) for md_page in list_md_page)

