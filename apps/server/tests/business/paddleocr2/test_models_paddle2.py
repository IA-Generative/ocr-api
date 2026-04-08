import os
import pytest
from PIL import Image
from src.schemas.output import Page
from business.paddleocr2.models.paddle import PaddleInferOCR2
from pathlib import Path


@pytest.fixture
def cache_dir() -> str:
    dir_path = os.environ.get("PADDLE_OCR_BASE_DIR", "/tmp")
    dir_path = Path(dir_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return str(dir_path)


def test_ocr_inference(cache_dir: str):
    obj = PaddleInferOCR2(path_model=cache_dir)
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)


def test_ocr_empty_image(cache_dir: str):
    obj = PaddleInferOCR2(path_model=cache_dir)
    # create an empty image
    image = Image.new("RGB", (100, 100), color=(255, 255, 255))

    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert len(actual_pages[0].boxes) == 0  # No boxes should be detected


def test_size_pages_not_align(cache_dir: str):
    obj = PaddleInferOCR2(path_model=cache_dir)
    image_path = "tests/data/valid/identite.jpg"
    image = Image.open(image_path).convert("RGB")
    with pytest.raises(AssertionError):
        obj.batch_predict(images=[image], pages=[Page(page=0), Page(page=1)])
