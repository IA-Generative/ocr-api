from typing import List
from time import time
from PIL import Image

from paddleocr import PPStructureV3
import numpy as np

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.logger import logger


class PaddleInferOCR2(BaseModelPrediction):
    def __init__(self, path_model: str):
        self.model: PPStructureV3 = PPStructureV3(
            use_doc_orientation_classify=True,
            use_doc_unwarping=False,
            use_textline_orientation=True,
            # Only run on regions the layout analysis detects as a table, so it
            # only adds latency on pages that contain one.
            use_table_recognition=True,
            use_formula_recognition=False,
            use_chart_recognition=False,
            use_seal_recognition=False,
            lang="fr",
            # PPStructureV3 only supports up to PP-OCRv5 (no PP-OCRv6 support yet).
            ocr_version="PP-OCRv5",
            # oneDNN's PIR executor can't convert the doc-orientation model's
            # array-of-double attributes on paddlepaddle 3.3.1, so disable it.
            enable_mkldnn=False,
        )

    def batch_predict(self, images: List[Image.Image], pages: list = [], *args, **kwargs) -> List[Page]:
        result: List[Page] = []
        if len(pages):
            assert len(images) == len(pages)

        for i, image in enumerate(images):
            width_img, height_img = image.size
            t = time()
            predictions = self.model.predict(np.array(image))
            logger.info(f"[PPStructureV3] Inference time: {time() - t:.2f}s")
            page_boxes: List[Bbox] = []
            page_markdowns = []

            for pred in predictions:
                ocr_res = pred["overall_ocr_res"]
                rec_texts = ocr_res["rec_texts"]
                rec_scores = ocr_res["rec_scores"]
                rec_boxes = ocr_res["rec_boxes"]
                rec_orientations = ocr_res.get("textline_orientation_angles") or [None] * len(rec_texts)

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
                        orientation=(int(orientation) if orientation is not None and orientation >= 0 else None),
                    )
                    page_boxes.append(box)

                page_markdowns.append(pred.markdown)

            markdown_info = self.model.concatenate_markdown_pages(page_markdowns)
            page = Page(page=i, boxes=page_boxes, page_markdown=markdown_info["markdown_texts"])
            result.append(page)

        return result
