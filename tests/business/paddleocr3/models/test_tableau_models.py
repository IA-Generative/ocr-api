import os
from PIL import Image
from src.schemas.output import Page
from src.schemas.layout import Layout
from business.paddleocr3.models.table import TablePrediction

DEVICE = os.environ.get("DEVICE", "cpu")


def test_table_inference_with_pages():
    obj = TablePrediction(device=DEVICE)
    image_path = "tests/data/valid/tableau.png"
    image = Image.open(image_path).convert("RGB")
    actual_pages = obj.batch_predict(
        images=[image],
        pages=[
            Page(
                page=0,
                layouts=[Layout(cls_id=1, label="table", score=1, coordinate=[0, 0, 1, 1])],
            )
        ],
    )
    assert len(actual_pages) == 1
    assert isinstance(actual_pages[0], Page)
    assert len(actual_pages[0].layouts) == 2
