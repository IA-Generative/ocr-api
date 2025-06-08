from abc import ABC, abstractmethod
from typing import List
from PIL import Image

from paddleocr import (
    LayoutDetection,
)
import numpy as np

from src.schemas.layout import Layout


class BaseLayoutDetection(ABC):
    @abstractmethod
    def predict(self, images: List[Image.Image], *args, **kwargs) -> List[List[Layout]]: ...


class PaddleLayoutDetection(BaseLayoutDetection):
    def __init__(self, model_name: str = "PP-DocLayout_plus-L", batch_size: int = 2, device: str = "cpu"):
        self.model = LayoutDetection(model_name=model_name, device=device, layout_nms=True)
        self.batch_size = batch_size

    def predict(self, images: List[Image.Image], *args, **kwargs) -> List[List[Layout]]:
        result: List[Layout] = []
        predictions = self.model.predict(
            [np.array(image.convert("RGB")) for image in images], batch_size=self.batch_size
        )

        for i, (image, pred) in enumerate(zip(images, predictions)):
            width_img, height_img = image.size
            page_layouts: List[Layout] = []
            bboxes = pred["boxes"]
            layouts = [Layout.model_validate(item) for item in bboxes]
            for i in range(len(layouts)):
                coordinates = layouts[i].coordinate
                coordinates[0] = coordinates[0] / width_img
                coordinates[2] = coordinates[2] / width_img
                coordinates[1] = coordinates[1] / height_img
                coordinates[3] = coordinates[3] / height_img
                layouts[i].coordinate = coordinates
                page_layouts.append(layouts[i])

            result.append(page_layouts)

        return result
