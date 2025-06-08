from PIL import Image
from pathlib import Path
from ocr_service.models.layout import PaddleLayoutDetection


def test_predict_paddle_layout_detections():
    obj = PaddleLayoutDetection()
    image = Image.open("tests/data/valid/formulaire-cerfa-complete.png")
    actuals = obj.predict(images=[image, image])

    assert len(actuals) == 2
    folder_image = Path("tests/data/valid/formulaire-cerfa-complete/layouts")
    folder_image.mkdir(parents=True, exist_ok=True)
    width_img, height_img = image.size
    i = 0
    for _, layouts in enumerate(actuals):
        for j, layout in enumerate(layouts):
            x1, y1, x2, y2 = layout.coordinate
            x1 = int(x1 * width_img)
            y1 = int(y1 * height_img)
            x2 = int(x2 * width_img)
            y2 = int(y2 * height_img)
            box = (x1, y1, x2, y2)
            cropped_image = image.crop(box)
            cropped_image.save(folder_image / f"{i}-{j}-{layout.label}-formulaire-cerfa-complete.png")
