import os 
import pytest
from PIL import Image
from src.schemas.output import Page
from business.paddleocr3.models.layout import PaddleLayoutDetection

DEVICE = os.environ.get("DEVICE", "cpu")

def test_layout_inference_without_pages():
    obj = PaddleLayoutDetection(device=DEVICE)
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)
    assert len(actual_pages[0].layouts) != 0


def test_layout_inference_with_pages():
    obj = PaddleLayoutDetection(device=DEVICE)
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    actual_pages = obj.batch_predict(images=[image], pages=[Page(page=0)])
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)
    assert len(actual_pages[0].layouts) != 0

    with pytest.raises(AssertionError):
        obj.batch_predict(images=[image], pages=[Page(page=0), Page(page=1)])
