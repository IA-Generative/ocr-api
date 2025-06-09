from PIL import Image
from pathlib import Path
from ocr_service.models.text import PaddleTextDetection, PaddleTextRecognition


def test_predict_paddle_text_detections():
    obj = PaddleTextDetection()
    image = Image.open("tests/data/valid/formulaire-cerfa-complete.png")
    actuals = obj.predict(images=[image, image])

    assert len(actuals) == 2
    folder_image = Path("tests/data/valid/formulaire-cerfa-complete")
    folder_image.mkdir(parents=True, exist_ok=True)
    width_img, height_img = image.size
    i = 0
    for _, bboxes in enumerate(actuals):
        for j, bbox in enumerate(bboxes):
            x1 = int(bbox.x * width_img)
            y1 = int(bbox.y * height_img)
            x2 = int((bbox.x + bbox.width) * width_img)
            y2 = int((bbox.y + bbox.height) * height_img)
            box = (x1, y1, x2, y2)
            cropped_image = image.crop(box)
            cropped_image.save(folder_image / f"{i}-{j}-formulaire-cerfa-complete.png")


def test_predict_paddle_text_recognition():
    obj = PaddleTextRecognition()
    image = Image.open("tests/data/valid/formulaire-cerfa-complete.png")
    actuals = obj.predict(images=[image, image])
    assert len(actuals) == 2
