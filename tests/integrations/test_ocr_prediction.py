import os
import json
from typing import Any, Dict

from PIL import Image
import numpy as np
import cv2

from ocr_service.models.paddle_ocr import PaddleInferOCR


import math


def assert_dict_almost_equal(d1: Dict[Any, Any], d2: Dict[Any, Any], tol: float = 1e-2):
    assert d1.keys() == d2.keys(), f"Les clés diffèrent : {d1.keys()} != {d2.keys()}"

    for key in d1:
        v1 = d1[key]
        v2 = d2[key]

        if isinstance(v1, float) and isinstance(v2, float):
            assert math.isclose(v1, v2, abs_tol=tol), (
                f"Différence sur clé '{key}': {v1} != {v2} avec tolérance {tol}"
            )

        elif isinstance(v1, list) and isinstance(v2, list):
            assert len(v1) == len(v2), (
                f"Listes de longueur différente pour clé '{key}': {len(v1)} != {len(v2)}"
            )
            for i, (x, y) in enumerate(zip(v1, v2)):
                if isinstance(x, float) and isinstance(y, float):
                    assert math.isclose(x, y, abs_tol=tol), (
                        f"Différence dans liste à l'index {i} pour clé '{key}': {x} != {y} avec tolérance {tol}"
                    )
                else:
                    assert x == y, (
                        f"Différence dans liste à l'index {i} pour clé '{key}': {x} != {y}"
                    )

        else:
            assert v1 == v2, f"Différence sur clé '{key}': {v1} != {v2}"


def test_integration_ocr_paddle_prediction():
    model = PaddleInferOCR("models/")
    filename = "tests/data/valid/identite.jpg"
    basename = os.path.basename(filename)
    base_file, _ = os.path.splitext(basename)
    image = Image.open(filename)
    output_folder = "tests/data/predictions/valid"
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
        for expect, actual in zip(expected, predictions):
            assert_dict_almost_equal(d1=expect, d2=actual.model_dump())

        cv2.imwrite(os.path.join(output_folder, f"{basename}"), image)
