import pytest
from PIL import Image
from src.schemas.output import Page
from business.checkbox_service.models.morpho import MorphoBoxDetection


def test_morpho_box_detection_inference():
    obj = MorphoBoxDetection()
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)


def test_morpho_size_pages_not_align():
    obj = MorphoBoxDetection()
    image_path = "tests/data/valid/identite.jpg"
    image = Image.open(image_path).convert("RGB")
    with pytest.raises(AssertionError):
        obj.batch_predict(images=[image], pages=[Page(page=0), Page(page=1)])
