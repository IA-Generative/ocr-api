import os
import pytest
from PIL import Image
from src.schemas.output import Page
from business.paddleocr2.models.paddle import PaddleInferOCR2


def test_ocr_inference():
    obj = PaddleInferOCR2(path_model=os.environ.get("PADDLE_OCR_BASE_DIR"))
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)


def test_size_pages_not_align():
    obj = PaddleInferOCR2(path_model=os.environ.get("PADDLE_OCR_BASE_DIR"))
    image_path = "tests/data/valid/identite.jpg"
    image = Image.open(image_path).convert("RGB")
    with pytest.raises(AssertionError):
        obj.batch_predict(images=[image], pages=[Page(page=0), Page(page=1)])
