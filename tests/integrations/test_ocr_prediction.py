import os
import json

from PIL import Image
import numpy as np
import cv2

from ocr_service.models.paddle_ocr import PaddleInferOCR


def test_integration_ocr_paddle_prediction():
    model = PaddleInferOCR("models/")
    filename = "tests/data/valid/identite.jpg"
    basename = os.path.basename(filename)
    base_file, _ = os.path.splitext(basename)
    image = Image.open(filename)
    output_folder = "tests/data/valid/predictions/"
    all_predictions = model.batch_predict([image])

    for predictions, image in zip(all_predictions, [image]):
        with open(os.path.join(output_folder, f"{base_file}.json"), "r") as f:
            expected = json.load(f)
        image = np.array(image)
        for pred in predictions:
            points = np.array(pred.text_region, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(
                image, [points], isClosed=True, color=(0, 255, 0), thickness=2
            )
            text = f"{pred.text} ({pred.confidence * 100:.1f}%)"
            text_position = (int(pred.text_region[0]), int(pred.text_region[1] - 10))
            cv2.putText(
                image,
                text,
                text_position,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )
        assert expected == [pred.model_dump() for pred in predictions]
        cv2.imwrite(os.path.join(output_folder, f"{basename}"), image)
