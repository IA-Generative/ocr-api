import os
from typing import List
from time import time
from PIL import Image

from paddleocr import PaddleOCR, LayoutDetection
from business.paddleocr2.configs.paddle import PaddleSetting
import numpy as np

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.layout import Layout
from src.schemas.box import Bbox
from src.logger import logger


paddle_settings = PaddleSetting()


class PaddleInferOCR2(BaseModelPrediction):
    def __init__(self, path_model: str = paddle_settings.PADDLE_PDX_CACHE_HOME):
        def _maybe_dir(p: str, sub: str):
            if not p:
                return None
            d = os.path.join(p, sub)
            return d if os.path.exists(d) else None

        det_dir = _maybe_dir(path_model, "detection")
        rec_dir = _maybe_dir(path_model, "recognition")

        # If specific model dirs are missing, pass None so PaddleOCR falls back
        # to built-in/official models or auto-downloads as per its logic.
        self.model: PaddleOCR = PaddleOCR(
            text_detection_model_dir=det_dir,
            text_recognition_model_dir=rec_dir,
            use_textline_orientation=False,
            use_doc_unwarping=False,
            lang="fr",
            ocr_version=paddle_settings.OCR_VERSION,
            device=paddle_settings.DEVICE,
            cpu_threads=paddle_settings.CPU_THREADS,
            enable_mkldnn=paddle_settings.ENABLE_MKLDNN,
        )
        self.warmup()

    def warmup(self):
        # Create a dummy white image for warmup
        dummy_image = Image.new("RGB", (640, 480), color="white")
        self.model.predict(np.array(dummy_image))

    def batch_predict(self, images: list[Image.Image], pages: list = [], *args, **kwargs) -> list[Page]:
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
                dt_polys = pred["dt_polys"]  # (N, 4, 2) — polygons in pixel coords
                rec_texts = pred["rec_texts"]
                rec_scores = pred["rec_scores"]
                if not (len(dt_polys) and len(rec_texts)):
                    continue
                for poly, text, score in zip(dt_polys, rec_texts, rec_scores):
                    # trans_poly_to_bbox: axis-aligned bbox from polygon points
                    pts = np.asarray(poly, dtype=float)  # (4, 2)
                    x1 = float(np.min(pts[:, 0]))
                    y1 = float(np.min(pts[:, 1]))
                    x2 = float(np.max(pts[:, 0]))
                    y2 = float(np.max(pts[:, 1]))

                    # Normalize coordinates between 0 and 1
                    norm_x = x1 / width_img
                    norm_y = y1 / height_img
                    norm_w = (x2 - x1) / width_img
                    norm_h = (y2 - y1) / height_img

                    box = Bbox(
                        x=norm_x,
                        y=norm_y,
                        width=norm_w,
                        height=norm_h,
                        confidence=float(score),
                        text=text,
                    )
                    page_boxes.append(box)

            page = Page(page=i, boxes=page_boxes)
            result.append(page)

        return result


class LayoutModel(BaseModelPrediction):
    def __init__(self, model_name: str = paddle_settings.LAYOUT_MODEL_NAME):
        # Placeholder for future layout model initialization
        self.model = LayoutDetection(model_name=model_name)  # Hypothetical layout detection model

    def batch_predict(self, images: list[Image.Image], pages: list[Page] = [], *args, **kwargs) -> list[Page]:
        # Placeholder for future layout model prediction logic
        result: list[Page] = []
        if len(pages):
            assert len(images) == len(pages), "Number of images and pages must match"

        for i, image in enumerate(images):
            npimage = np.array(image)
            output = self.model.predict(
                npimage,
                batch_size=1,
                layout_nms=True,
            )
            layouts: list[Layout] = []
            for res in output:
                for box in res["boxes"]:
                    layouts.append(Layout.model_validate(box))
            pages[i].layouts = layouts
            result.append(pages[i])
        return result
