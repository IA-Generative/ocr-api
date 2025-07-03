from typing import List, Union
from PIL import Image

from paddleocr import (
    LayoutDetection,
)
import numpy as np

from src.schemas.layout import Layout
from src.schemas.output import Page
from services.base.model import BaseModelPrediction


class PaddleLayoutDetection(BaseModelPrediction):
    def __init__(
        self,
        model_name: str = "PP-DocLayout_plus-L",
        batch_size: int = 2,
        device: str = "cpu",
    ):
        self.model = LayoutDetection(model_name=model_name, device=device, layout_nms=True)
        self.batch_size = batch_size

    def batch_predict(
        self,
        images: list[Union[np.ndarray, Image.Image]],
        pages: list[Page] = [],
    ) -> List[Page]:
        result: List[Page] = []
        if len(pages):
            assert len(images) == len(pages)
            result = pages
        else:
            result = [Page(page=i, layouts=[]) for i in range(len(images))]

        predictions = self.model.predict(
            [np.array(image.convert("RGB")) for image in images],
            batch_size=self.batch_size,
        )

        for index_page, (image, pred) in enumerate(zip(images, predictions)):
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

            result[index_page].layouts = page_layouts

        return result
