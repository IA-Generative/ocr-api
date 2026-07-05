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
    assert len(actual_pages[0].boxes) > 0


def test_ocr_empty_image():
    obj = PaddleInferOCR2(path_model=os.environ.get("PADDLE_OCR_BASE_DIR"))
    # create an empty image
    image = Image.new("RGB", (100, 100), color=(255, 255, 255))

    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert len(actual_pages[0].boxes) == 0  # No boxes should be detected


def test_size_pages_not_align():
    obj = PaddleInferOCR2(path_model=os.environ.get("PADDLE_OCR_BASE_DIR"))
    image_path = "tests/data/valid/identite.jpg"
    image = Image.open(image_path).convert("RGB")
    with pytest.raises(AssertionError):
        obj.batch_predict(images=[image], pages=[Page(page=0), Page(page=1)])
