from typing import List
import logging
from PIL import Image
import numpy as np
import time

from src.schemas.layout import Layout
from src.schemas.output import Page
from services.base.model import BaseModelPrediction

from paddleocr import FormulaRecognition
from src.logger import logger

logger.setLevel(logging.DEBUG)


def crop_img(img: Image.Image, coordinates: list[float], is_normalized: bool = True):
    if is_normalized:
        width_img, height_img = img.size
        coordinates[0] = coordinates[0] * width_img
        coordinates[2] = coordinates[2] * width_img
        coordinates[1] = coordinates[1] * height_img
        coordinates[3] = coordinates[3] * height_img

    left, upper, right, lower = map(int, coordinates)

    return img.crop((left, upper, right, lower))


class PaddleFormulaRecognizer(BaseModelPrediction):
    def __init__(
        self,
        model_name: str = "PP-FormulaNet_plus-M",
        device: str = "cpu",
        batch_size: int = 1,
    ):
        logger.debug("FormulaRecognition start")
        self.model = FormulaRecognition(model_name=model_name, device=device)
        logger.info("FormulaRecognition init")
        self.batch_size = batch_size

    def batch_predict(
        self,
        images: list[Image.Image],
        pages: list[Page] = [],
    ) -> List[Page]:
        if len(pages):
            assert len(pages) == len(images)
        else:
            pages = [
                Page(
                    page=i,
                    layouts=[
                        Layout(
                            cls_id=1,
                            label="formula",
                            score=1,
                            coordinate=[0, 0, 1, 1],
                        ),
                    ],
                )
                for i in range(len(images))
            ]

        for j, (page, image) in enumerate(zip(pages, images)):
            layouts = page.layouts
            logger.debug(f"[Formula] nb layouts {len(layouts)}")
            formula_layouts: list[Layout] = []
            formula_layouts_indices = []
            for i, layout in enumerate(layouts):
                if layout.label == "formula":
                    formula_layouts_indices.append(i)
                    formula_layouts.append(layout)
            logger.debug(f"[Formula] nb formula layouts {len(formula_layouts_indices)}")
            formula_crop_images: list[Image.Image] = []
            for formula_layout in formula_layouts:
                crop_image = crop_img(image, coordinates=formula_layout.coordinate, is_normalized=True)
                formula_crop_images.append(crop_image)
            logger.debug(f"[Formula] nb images layouts {len(formula_crop_images)}")
            t = time.time()
            result = self.model.predict(
                [np.array(image.convert("RGB")) for image in formula_crop_images],
                batch_size=self.batch_size,
            )
            total_time = time.time() - t
            logger.debug(f"[Formula] time to process {len(formula_crop_images)} - {total_time:.3f}s")

            for i, res in enumerate(result):
                layouts[i].content = res["rec_formula"]

            page.layouts = layouts
            pages[j] = page

        return pages
