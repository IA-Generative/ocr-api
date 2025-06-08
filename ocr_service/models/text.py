from abc import ABC, abstractmethod
from typing import List
from PIL import Image

from paddleocr import TextDetection
import numpy as np

from src.schemas.box import BaseBox


class BaseTextDetection(ABC):
    @abstractmethod
    def predict(self, images: list[Image.Image]): ...


class BaseTextRecognition:
    @abstractmethod
    def predict(self, images: List[Image.Image]): ...


class PaddleTextDetection(BaseTextDetection):
    def __init__(
        self,
        model_name: str = "PP-OCRv5_server_det",
        device: str = "cpu",
        batch_size: int = 1,
    ):
        self.model_text_detection = TextDetection(model_name=model_name, device=device)
        self.batch_size = batch_size

    def predict(self, images: list[Image.Image]) -> list[List[BaseBox]]:
        data = self.model_text_detection.predict(
            [np.array(image.convert("RGB")) for image in images],
            batch_size=self.batch_size,
        )
        # dt_polys: Predicted text detection boxes, where each box contains four vertices (x, y coordinates).
        # dt_scores: Confidence scores of the predicted text detection boxes.
        total_bboxes = []
        for i, (image, prediction) in enumerate(zip(images, data)):
            width_img, height_img = image.size
            confidences = prediction["dt_scores"]
            bboxes = prediction["dt_polys"]
            res_bboxes: List[BaseBox] = []
            for bbox, confidence in zip(bboxes, confidences):
                # Convert polygon to bounding box

                x_coords = [pt[0] for pt in bbox]
                y_coords = [pt[1] for pt in bbox]
                x = min(x_coords) / width_img
                y = min(y_coords) / height_img
                w = max(x_coords) - x
                w = w / width_img
                h = max(y_coords) - y
                h = h / height_img
                res_bboxes.append(BaseBox(x=x, y=y, width=w, height=h, confidence=confidence))
            total_bboxes.append(res_bboxes)

        return total_bboxes
