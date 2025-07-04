import os 
from PIL import Image
from src.schemas.output import Page
from business.paddleocr3.models.formula import PaddleFormulaPredcition

DEVICE = os.environ.get("DEVICE", "cpu")

def test_formula_inference_without_pages():
    obj = PaddleFormulaPredcition(device=DEVICE)
    image_path = "tests/data/valid/formule.png"
    image = Image.open(image_path).convert("RGB")
    actual_pages = obj.batch_predict(images=[image])
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)
    assert len(actual_pages[0].layouts) != 0
    assert actual_pages[0].layouts[0].content is not None
    assert actual_pages[0].layouts[0].content == "P_{n}(X)={\\frac{1}{2^{n}n!}}((X^{2}-1)^{n})^{(n)}"
