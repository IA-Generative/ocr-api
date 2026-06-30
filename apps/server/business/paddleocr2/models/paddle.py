import os
from typing import List
from time import time
from PIL import Image

from paddleocr import PaddleOCR
import numpy as np

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.logger import logger


class PaddleInferOCR2(BaseModelPrediction):
    def __init__(self, path_model: str):
        self.model: PaddleOCR = PaddleOCR(
            use_doc_orientation_classify=True,
            use_doc_unwarping=False,
            use_textline_orientation=True,
            engine="paddle",
            lang="fr",
            ocr_version="PP-OCRv6",
            # oneDNN's PIR executor can't convert the doc-orientation model's
            # array-of-double attributes on paddlepaddle 3.3.1, so disable it.
            enable_mkldnn=False,
        )

    def batch_predict(
        self, images: List[Image.Image], pages: list = [], *args, **kwargs
    ) -> List[Page]:
        result: List[Page] = []
        if len(pages):
            assert len(images) == len(pages)

        for i, image in enumerate(images):
            width_img, height_img = image.size
            t = time()
            predictions = self.model.predict(
                np.array(image), use_doc_orientation_classify=True
            )
            logger.info(f"[PaddleOCR] Inference time: {time() - t:.2f}s")
            page_boxes: List[Bbox] = []

            for pred in predictions:
                rec_texts = pred["rec_texts"]
                rec_scores = pred["rec_scores"]
                rec_boxes = pred["rec_boxes"]
                rec_orientations = pred.get("textline_orientation_angles") or [
                    None
                ] * len(rec_texts)

                for text, confidence, box_coords, orientation in zip(
                    rec_texts, rec_scores, rec_boxes, rec_orientations
                ):
                    x_min, y_min, x_max, y_max = box_coords
                    w = x_max - x_min
                    h = y_max - y_min

                    # Normalize coordinates between 0 and 1
                    norm_x = x_min / width_img
                    norm_y = y_min / height_img
                    norm_w = w / width_img
                    norm_h = h / height_img

                    box = Bbox(
                        x=norm_x,
                        y=norm_y,
                        width=norm_w,
                        height=norm_h,
                        confidence=float(confidence),
                        text=text,
                        orientation=(
                            int(orientation)
                            if orientation is not None and orientation >= 0
                            else None
                        ),
                    )
                    page_boxes.append(box)

            page = Page(page=i, boxes=page_boxes)
            result.append(page)

        return result
