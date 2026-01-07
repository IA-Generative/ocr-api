from typing import List
from time import time
from PIL import Image

from paddleocr import PPStructureV3
import numpy as np

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.logger import logger


class PPStructureV3fix(PPStructureV3):
    def __init__(self, layout_detection_model_name=None, layout_detection_model_dir=None, layout_threshold=None, layout_nms=None, layout_unclip_ratio=None, layout_merge_bboxes_mode=None, chart_recognition_model_name=None, chart_recognition_model_dir=None, chart_recognition_batch_size=None, region_detection_model_name=None, region_detection_model_dir=None, doc_orientation_classify_model_name=None, doc_orientation_classify_model_dir=None, doc_unwarping_model_name=None, doc_unwarping_model_dir=None, text_detection_model_name=None, text_detection_model_dir=None, text_det_limit_side_len=None, text_det_limit_type=None, text_det_thresh=None, text_det_box_thresh=None, text_det_unclip_ratio=None, textline_orientation_model_name=None, textline_orientation_model_dir=None, textline_orientation_batch_size=None, text_recognition_model_name=None, text_recognition_model_dir=None, text_recognition_batch_size=None, text_rec_score_thresh=None, table_classification_model_name=None, table_classification_model_dir=None, wired_table_structure_recognition_model_name=None, wired_table_structure_recognition_model_dir=None, wireless_table_structure_recognition_model_name=None, wireless_table_structure_recognition_model_dir=None, wired_table_cells_detection_model_name=None, wired_table_cells_detection_model_dir=None, wireless_table_cells_detection_model_name=None, wireless_table_cells_detection_model_dir=None, table_orientation_classify_model_name=None, table_orientation_classify_model_dir=None, seal_text_detection_model_name=None, seal_text_detection_model_dir=None, seal_det_limit_side_len=None, seal_det_limit_type=None, seal_det_thresh=None, seal_det_box_thresh=None, seal_det_unclip_ratio=None, seal_text_recognition_model_name=None, seal_text_recognition_model_dir=None, seal_text_recognition_batch_size=None, seal_rec_score_thresh=None, formula_recognition_model_name=None, formula_recognition_model_dir=None, formula_recognition_batch_size=None, use_doc_orientation_classify=None, use_doc_unwarping=None, use_textline_orientation=None, use_seal_recognition=None, use_table_recognition=None, use_formula_recognition=None, use_chart_recognition=None, use_region_detection=None, lang=None, ocr_version=None, **kwargs):
        super().__init__(layout_detection_model_name, layout_detection_model_dir, layout_threshold, layout_nms, layout_unclip_ratio, layout_merge_bboxes_mode, chart_recognition_model_name, chart_recognition_model_dir, chart_recognition_batch_size, region_detection_model_name, region_detection_model_dir, doc_orientation_classify_model_name, doc_orientation_classify_model_dir, doc_unwarping_model_name, doc_unwarping_model_dir, text_detection_model_name, text_detection_model_dir, text_det_limit_side_len, text_det_limit_type, text_det_thresh, text_det_box_thresh, text_det_unclip_ratio, textline_orientation_model_name, textline_orientation_model_dir, textline_orientation_batch_size, text_recognition_model_name, text_recognition_model_dir, text_recognition_batch_size, text_rec_score_thresh, table_classification_model_name, table_classification_model_dir, wired_table_structure_recognition_model_name, wired_table_structure_recognition_model_dir,
                         wireless_table_structure_recognition_model_name, wireless_table_structure_recognition_model_dir, wired_table_cells_detection_model_name, wired_table_cells_detection_model_dir, wireless_table_cells_detection_model_name, wireless_table_cells_detection_model_dir, table_orientation_classify_model_name, table_orientation_classify_model_dir, seal_text_detection_model_name, seal_text_detection_model_dir, seal_det_limit_side_len, seal_det_limit_type, seal_det_thresh, seal_det_box_thresh, seal_det_unclip_ratio, seal_text_recognition_model_name, seal_text_recognition_model_dir, seal_text_recognition_batch_size, seal_rec_score_thresh, formula_recognition_model_name, formula_recognition_model_dir, formula_recognition_batch_size, use_doc_orientation_classify, use_doc_unwarping, use_textline_orientation, use_seal_recognition, use_table_recognition, use_formula_recognition, use_chart_recognition, use_region_detection, lang, ocr_version, **kwargs)

        self._params["layout_detection_model_name"] = layout_detection_model_name
        self._params["layout_detection_model_dir"] = layout_detection_model_dir
        self._params["layout_threshold"] = layout_threshold
        self._params["layout_nms"] = layout_nms
        self._params["layout_unclip_ratio"] = layout_unclip_ratio
        self._params["layout_merge_bboxes_mode"] = layout_merge_bboxes_mode
        self._params["chart_recognition_model_name"] = chart_recognition_model_name
        self._params["chart_recognition_model_dir"] = chart_recognition_model_dir
        self._params["chart_recognition_batch_size"] = chart_recognition_batch_size
        self._params["region_detection_model_name"] = region_detection_model_name
        self._params["region_detection_model_dir"] = region_detection_model_dir
        self._params["doc_orientation_classify_model_name"] = doc_orientation_classify_model_name
        self._params["doc_orientation_classify_model_dir"] = doc_orientation_classify_model_dir
        self._params["doc_unwarping_model_name"] = doc_unwarping_model_name
        self._params["doc_unwarping_model_dir"] = doc_unwarping_model_dir
        self._params["text_detection_model_name"] = text_detection_model_name
        self._params["text_detection_model_dir"] = text_detection_model_dir
        self._params["text_det_limit_side_len"] = text_det_limit_side_len
        self._params['use_chart_recognition'] = use_chart_recognition


class PPStructureInferV5(BaseModelPrediction):
    def __init__(self, **options):
        chart_recognition_model_name = None
        chart_recognition_model_dir = None

        self.model: PPStructureV3 = PPStructureV3fix(
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
