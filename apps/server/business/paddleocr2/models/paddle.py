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
        def _maybe_dir(p: str, sub: str):
            if not p:
                return None
            d = os.path.join(p, sub)
            return d if os.path.exists(d) else None

        det_dir = _maybe_dir(path_model, "detection")
        rec_dir = _maybe_dir(path_model, "recognition")
        cls_dir = _maybe_dir(path_model, "classification")

        # If specific model dirs are missing, pass None so PaddleOCR falls back
        # to built-in/official models or auto-downloads as per its logic.
        self.model: PaddleOCR = PaddleOCR(
            text_detection_model_dir=det_dir,
            text_recognition_model_dir=rec_dir,
            textline_orientation_model_dir=cls_dir,
            use_textline_orientation=True if cls_dir is not None else False,
            lang="fr",
            ocr_version="PP-OCRv3",
        )

    def batch_predict(
        self, images: list[Image.Image], pages: list = [], *args, **kwargs
    ) -> list[Page]:
        result: list[Page] = []
        if len(pages):
            assert len(images) == len(pages), "Number of images and pages must match"

        for i, image in enumerate(images):
            width_img, height_img = image.size
            t = time()
            predictions = self.model.predict(np.array(image))
            logger.info(f"[PaddleOCR] Inference time: {time() - t:.2f}s")
            page_boxes: List[Bbox] = []

            for pred in predictions:
                rec_scores = pred["rec_scores"]
                rec_boxes = pred["rec_boxes"]
                # textline_orientation_angles = pred["textline_orientation_angles"]
                rec_texts = pred["rec_texts"]
                if pred is not None and len(pred):
                    for rec_score, rec_text, bbox in zip(
                        rec_scores, rec_texts, rec_boxes
                    ):
                        text = rec_text

                        # Convert polygon to bounding box

                        x = bbox[0]
                        y = bbox[1]
                        w = bbox[2] - bbox[0]
                        h = bbox[3] - bbox[1]

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
                            confidence=float(rec_score),
                            text=text,
                        )
                        page_boxes.append(box)

            page = Page(page=i, boxes=page_boxes)
            result.append(page)

        return result
