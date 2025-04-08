import numpy as np
from src.services.paddle_ocr import OCRCustom
from src.schemas.inference import TextBox
from PIL import Image
import numpy as np


def test_perform_ocr():

    # Instantiate the class (no real models loaded due to mock)
    ocr = OCRCustom()
    image = Image.open(
        "tests/data/valid/formulaire-cerfa-complete.png")

    image = np.array(image)

    # Run OCR
    result = ocr.perform_ocr(image)

    # Check results
    assert len(result) > 0
    assert len(result[0]) > 1
