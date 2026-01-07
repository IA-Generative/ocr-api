from typing import List
from time import time
from PIL import Image

from paddleocr import PPStructureV3
import numpy as np

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.logger import logger


class PPStructureInferV5(BaseModelPrediction):
    def __init__(self, **options):
        chart_recognition_model_name = None
        chart_recognition_model_dir = None

        self.model: PPStructureV3 = PPStructureV3(
            # text_detection_model_name=options.get(
            #     "text_detection_model_name", "PP-OCRv5_mobile_det"),
            # text_recognition_model_name=options.get(
            #     "text_recognition_model_name", "PP-OCRv5_mobile_rec"),

            use_chart_recognition=options.get("use_chart_recognition", False),
            use_doc_orientation_classify=options.get(
                "use_doc_orientation_classify", True),
            use_table_recognition=options.get("use_table_recognition", True),
            use_doc_unwarping=options.get("use_doc_unwarping", False),
            use_formula_recognition=options.get(
                "use_formula_recognition", False),
            use_textline_orientation=options.get(
                "use_textline_orientation", False),
            use_region_detection=options.get("use_region_detection", True),
            use_seal_recognition=options.get("use_seal_recognition", False),
            lang=options.get("lang", "fr"),

            device=options.get("device", "cpu"),
            chart_recognition_model_name=chart_recognition_model_name,
            chart_recognition_model_dir=chart_recognition_model_dir
        )
        self._options = options

    def batch_predict(self, images: List[Image.Image], pages: list = [], *args, **kwargs) -> List[Page]:
        result: List[Page] = []
        if len(pages):
            assert len(images) == len(pages)

        for i, image in enumerate(images):
            width_img, height_img = image.size
            t = time()
            predictions = self.model.predict(np.array(
                image), use_chart_recognition=self._options.get("use_chart_recognition", False),
                use_formula_recognition=self._options.get(
                    "use_formula_recognition", False),
                use_ocr_results_with_table_cells=self._options.get(
                    "use_ocr_results_with_table_cells", True),
                use_doc_orientation_classify=self._options.get(
                    "use_doc_orientation_classify", True),
                use_doc_unwarping=self._options.get(
                    "use_doc_unwarping", False),
                use_textline_orientation=self._options.get(
                    "use_textline_orientation", False),
                use_region_detection=self._options.get(
                    "use_region_detection", True),
                use_seal_recognition=self._options.get(
                    "use_seal_recognition", False)

            )
            logger.info(f"[PaddleOCR] Inference time: {time() - t:.2f}s")
            page_boxes: List[Bbox] = []

            for pred in predictions:
                print(pred.keys())
                sub_pred = pred['overall_ocr_res']
                for bbox, text, score in zip(sub_pred["rec_boxes"], sub_pred["rec_texts"], sub_pred["rec_scores"]):
                    if sub_pred is not None and score > 0:
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
                            confidence=float(score),
                            text=text,
                        )
                        page_boxes.append(box)

            page = Page(page=i, boxes=page_boxes,
                        markdown=pred.markdown.get("markdown_texts", None))

            if kwargs.get('save_markdown', None):
                pred.save_to_markdown(kwargs.get('save_markdown'))
            if kwargs.get('save_json', None):
                pred.save_to_json(kwargs.get('save_json'))

            if kwargs.get('save_visualization', None):
                vis_path = kwargs.get('save_visualization')
                pred.save_to_img(vis_path)

            result.append(page)

        return result
