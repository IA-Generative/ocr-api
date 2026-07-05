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
        self.model = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            lang="fr",
            ocr_version="PP-OCRv5",
            device="cpu",
        )

    def batch_predict(self, images: List[Image.Image], pages: list = [], *args, **kwargs) -> List[Page]:
        result: List[Page] = []
        if len(pages):
            assert len(images) == len(pages)

        for i, image in enumerate(images):
            width_img, height_img = image.size
            t = time()
            predictions = list(self.model.predict(np.array(image)))
            logger.info(f"[PaddleOCR] Inference time: {time() - t:.2f}s")
            page_boxes: List[Bbox] = []

            if predictions:
                pred = predictions[0]
                rec_texts = pred["rec_texts"]
                rec_scores = pred["rec_scores"]
                rec_boxes = pred["rec_boxes"]  # [x_min, y_min, x_max, y_max] absolute px

                for text, confidence, box_coords in zip(rec_texts, rec_scores, rec_boxes):
                    x_min, y_min, x_max, y_max = box_coords
                    box = Bbox(
                        x=x_min / width_img,
                        y=y_min / height_img,
                        width=(x_max - x_min) / width_img,
                        height=(y_max - y_min) / height_img,
                        confidence=float(confidence),
                        text=text,
                    )
                    page_boxes.append(box)

            page = Page(page=i, boxes=page_boxes)
            result.append(page)

        return result
