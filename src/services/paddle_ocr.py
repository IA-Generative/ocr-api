import base64
import io
import os
from typing import List
from paddleocr import PaddleOCR
import numpy as np
from pathlib import Path
from ..schemas.inference import TextBox

path_model = Path(os.getenv("MODEL_PATH", Path(__file__).parent.absolute()))


class OCRCustom:
    def __init__(self, model_dir: Path = path_model):
        self.ocr_model = PaddleOCR(
            det_model_dir=str(model_dir / "detection"),
            rec_model_dir=str(model_dir / "recognition"),
            cls_model_dir=str(model_dir / "recognition"),
            use_angle_cls=False,
            lang="fr",
        )

    @property
    def __version__(self):
        return
    # Helper function: Perform OCR and format result

    def perform_ocr(self, img_array: np.ndarray) -> List[List[TextBox]]:
        results = self.ocr_model.ocr(img_array)
        final_result = []
        for result in results:
            tmp_result = []
            if result:
                for bbox, (text, confidence) in result:
                    tmp_result.append(dict(confidence=round(
                        confidence, 2), text=text, text_region=[[int(x), int(y)] for x, y in bbox]))

                final_result.append(tmp_result)

        return final_result


# Helper function: Convert image to base64
def image_to_base64(image, format="PNG"):
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
