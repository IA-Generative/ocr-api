from PIL import Image
from ocr_service.models.paddle_ocr import PaddleInferOCR
from src.schemas.output import Page


def test_predict():
    image = Image.open("tests/data/valid/formulaire-cerfa-complete.png")

    obj = PaddleInferOCR()
    for _ in range(5):
        actuals = obj.batch_predict(images=[image])

        assert len(actuals) == 1
        for actual in actuals:
            assert isinstance(actual, Page)
