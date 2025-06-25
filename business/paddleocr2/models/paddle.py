import os
from typing import List
import logging
from PIL import Image

from paddleocr import PaddleOCR
import numpy as np

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.logger import logger

logger.setLevel(logging.DEBUG)


class PaddleInferOCR2(BaseModelPrediction):
    def __init__(self, path_model: str):
        self.model: PaddleOCR = PaddleOCR(
            det_model_dir=os.path.join(path_model, "detection"),
            rec_model_dir=os.path.join(path_model, "recognition"),
            cls_model_dir=os.path.join(path_model, "classification"),
            use_angle_cls=False,
            lang="fr",
        )

    def batch_predict(self, images: List[Image.Image], pages: list = [], *args, **kwargs) -> List[Page]:
        result: List[Page] = []
        if len(pages):
            assert len(images) == len(pages)

        for i, image in enumerate(images):
            width_img, height_img = image.size
            predictions = self.model.ocr(np.array(image), det=True, rec=True, cls=True)
            page_boxes: List[Bbox] = []

            for pred in predictions:
                for text_pred in pred:
                    bbox, (text, confidence) = text_pred

                    # Convert polygon to bounding box
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    x = min(x_coords)
                    y = min(y_coords)
                    w = max(x_coords) - x
                    h = max(y_coords) - y

                    # Normalize coordinates between 0 and 1
                    norm_x = x / width_img
                    norm_y = y / height_img
                    norm_w = w / width_img
                    norm_h = h / height_img

                    box = Bbox(
                        x=norm_x,
                        y=norm_y,
                        width=norm_w,
                        height=norm_h,
                        confidence=float(confidence),
                        text=text,
                    )
                    page_boxes.append(box)

            page = Page(page=i, boxes=page_boxes)
            result.append(page)

        return result
