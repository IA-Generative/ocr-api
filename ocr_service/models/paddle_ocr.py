from typing import List
from PIL import Image

from paddleocr import PaddleOCR
import numpy as np

from ocr_service.models.base import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.box import Bbox


class PaddleInferOCR(BaseModelPrediction):
    def __init__(self, device: str = "cpu"):
        self.model: PaddleOCR = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            ocr_version="PP-OCRv5",
            device=device,
        )

    def batch_predict(self, images: List[Image.Image], *args, **kwargs) -> List[Page]:
        result: List[Page] = []

        for i, image in enumerate(images):
            width_img, height_img = image.size
            image = image.convert("RGB")
            predictions = self.model.predict(np.array(image))
            page_boxes: List[Bbox] = []
            # rec_text: Indicates the predicted text of the text line image.
            # rec_score: Indicates the confidence score of the predicted text for the text line image.
            # dt_polys: Predicted text detection boxes, where each box contains four vertices (x, y coordinates).
            # dt_scores: Confidence scores of the predicted text detection boxes.

            for pred in predictions:
                bboxes = pred["rec_boxes"]
                confidences = pred["rec_scores"]
                texts = pred["rec_texts"]
                for bbox, confidence, text in zip(bboxes, confidences, texts):
                    # Convert polygon to bounding box
                    x_coords = [bbox[0], bbox[2]]
                    y_coords = [bbox[1], bbox[3]]
                    x = min(x_coords)
                    y = min(y_coords)
                    w = max(x_coords) - x
                    h = max(y_coords) - y

                    # Normalize coordinates between 0 and 1
                    norm_x = x / width_img
                    norm_y = y / height_img
                    norm_w = w / width_img
                    norm_h = h / height_img

                    box = Bbox(x=norm_x, y=norm_y, width=norm_w, height=norm_h, confidence=float(confidence), text=text)
                    page_boxes.append(box)

            page = Page(page=i, boxes=page_boxes)
            result.append(page)

        return result
