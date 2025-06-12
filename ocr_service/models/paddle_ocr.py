from typing import List
import logging
from PIL import Image, ImageOps
from time import perf_counter

from paddleocr import PaddleOCR
import numpy as np

from ocr_service.models.base import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.box import Bbox
from paddleocr import logger

logger.setLevel(logging.DEBUG)


class PaddleInferOCR(BaseModelPrediction):
    def __init__(
        self,
        device: str = "cpu",
        cpu_threads: int = 4,
        batch_size: int = 1,
        target_size: int = 960,
        text_detection_model_name: str = None,  # "PP-OCRv5_mobile_det"
        text_recognition_model_name: str = None,  # "PP-OCRv5_mobile_rec"
        ocr_version: str = "PP-OCRv3",
        lang: str | None = None,
    ):
        self.preserve_aspect_ratio = True
        self.device = device
        self.cpu_threads = cpu_threads
        self.text_detection_model_name = text_detection_model_name
        self.text_recognition_model_name = text_recognition_model_name
        self.ocr_version = ocr_version
        self.lang = lang

        self.target_size = target_size
        self.model: PaddleOCR = None
        self.batch_size = batch_size
        self._counter_pred = 0
        self._initialize_model()

        logger.debug("Warmup start")
        t = perf_counter()
        self.model.predict(np.zeros((100, 100, 3), dtype=np.uint8))
        logger.debug(f"Warmup end into {perf_counter() -t}")
        t = perf_counter()
        self.model.predict(np.zeros((100, 100, 3), dtype=np.uint8))
        logger.debug(f"Warmup end into {perf_counter() -t}")

    def _initialize_model(self):
        logger.debug(f"Init model at {self._counter_pred} predictions")
        self.model: PaddleOCR = PaddleOCR(
            text_detection_model_name=self.text_detection_model_name,
            text_recognition_model_name=self.text_recognition_model_name,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            # use_textline_orientation
            ocr_version=self.ocr_version,
            device=self.device,
            # cpu_threads=max(1, self.cpu_threads - 1),
            # text_det_limit_side_len=960,
            # text_det_limit_type="max",
            # text_recognition_batch_size=12,
            # enable_mkldnn=True,
            # text_det_limit_side_len=self.target_size,  # Synchroniser avec la taille de redimensionnement
            # text_det_limit_type="min",  # Redimensionner basé sur le côté le plus long
            # det_db_score_mode="fast",
            lang=self.lang,
        )

    def _resize_image(self, image: Image.Image) -> Image.Image:
        """Redimensionne l'image tout en préservant le ratio d'aspect si demandé"""
        if self.target_size:
            if self.preserve_aspect_ratio:
                return ImageOps.contain(image, (self.target_size, self.target_size))
            else:
                return image.resize((self.target_size, self.target_size), Image.LANCZOS)
        return image

    def batch_predict(self, images: List[Image.Image], *args, **kwargs) -> List[Page]:
        result: List[Page] = []
        t_resize = perf_counter()
        resized_images = [self._resize_image(img) for img in images]
        logger.debug(f"Resize time {perf_counter() - t_resize}")
        converted_images = [np.array(image.convert("RGB")) for image in resized_images]
        logger.debug(f"Nb image to predicts: {len(images)}")
        t = perf_counter()
        predictions = self.model.predict(converted_images)
        logger.debug(f"Time to process {len(images)}: {perf_counter() - t}")

        for i, (image, pred) in enumerate(zip(images, predictions)):
            width_img, height_img = image.size
            page = Page(page=i, boxes=[])
            # rec_text: Indicates the predicted text of the text line image.
            # rec_score: Indicates the confidence score of the predicted text for the text line image.
            # dt_polys: Predicted text detection boxes, where each box contains four vertices (x, y coordinates).
            # dt_scores: Confidence scores of the predicted text detection boxes.

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

                box = Bbox(
                    x=norm_x,
                    y=norm_y,
                    width=norm_w,
                    height=norm_h,
                    confidence=float(confidence),
                    text=text,
                )
                page.boxes.append(box)

            result.append(page)
        self._counter_pred += len(result)
        if self._counter_pred % 4 == 0:
            self._initialize_model()
            self._counter_pred = 0

        return result
