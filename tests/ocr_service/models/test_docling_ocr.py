from PIL import Image
from src.schemas.output import MarkdownPage
from io import BytesIO


def test_predict():
    from ocr_service.models.docling_ocr import DoclingInferOCR

    image = Image.open("tests/data/valid/formulaire-cerfa-complete.png")

    obj = DoclingInferOCR()

    list_md_page: list[MarkdownPage] = obj.batch_predict([image])

    assert len(list_md_page)
    assert all(isinstance(md_page, MarkdownPage) for md_page in list_md_page)
