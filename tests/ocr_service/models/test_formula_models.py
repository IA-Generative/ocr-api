from PIL import Image
from ocr_service.models.formula import PaddleFormulaPredcition


def test_predict_paddle_layout_detections():
    obj = PaddleFormulaPredcition()
    image = Image.open("tests/data/valid/general_formula_rec_001_res_paddleocr3.png")
    actuals = obj.predict(images=[image])

    assert len(actuals) == 1
