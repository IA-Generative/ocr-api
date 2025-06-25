import pytest
from PIL import Image
from src.schemas.output import Page
from business.checkbox_service.models.box_detection import BoxDetection


def test_box_detection_inference():
    obj = BoxDetection()
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)


def test_size_pages_not_align():
    obj = BoxDetection()
    image_path = "tests/data/valid/identite.jpg"
    image = Image.open(image_path).convert("RGB")
    with pytest.raises(AssertionError):
        obj.batch_predict(images=[image], pages=[Page(page=0), Page(page=1)])
