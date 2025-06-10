from PIL import Image
from pathlib import Path
from ocr_service.models.layout import PaddleLayoutDetection
from src.utils.draw import draw_normalized_layout


def test_predict_paddle_layout_detections():
    obj = PaddleLayoutDetection()
    path_image = Path("tests/data/valid/formulaire-cerfa-complete.png")
    image = Image.open(path_image)
    actuals = obj.predict(images=[image, image])

    assert len(actuals) == 2
    folder_image = Path("tests/data/valid/formulaire-cerfa-complete/layouts")
    folder_image.mkdir(parents=True, exist_ok=True)

    for layouts in actuals:
        image = draw_normalized_layout(image, layouts=layouts)
        image.save(folder_image / f"{path_image.stem}{path_image.suffix}")
