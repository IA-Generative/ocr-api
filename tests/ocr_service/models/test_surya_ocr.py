from PIL import Image
from ocr_service.configs.surya import SuryaSetting
from ocr_service.models.surya_ocr import SuryaOCR
from src.schemas.prediction import PredictionOCR


def test_predict():
    settings = SuryaSetting()
    image = Image.open("tests/data/valid/formulaire-cerfa-complete.png")

    obj = SuryaOCR(
        checkpoint_detection=settings.SURYA_DETECTION_FOLDER,
        checkpoint_recognition=settings.SURYA_RECOGNITION_FOLDER,
    )
    actuals = obj.batch_predict(images=[image, image], langs=[["fr"], ["fr", "en"]])

    assert len(actuals) == 2
    for actual in actuals:
        for instance in actual:
            assert isinstance(instance, PredictionOCR)
