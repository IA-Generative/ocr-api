from PIL import Image
import numpy as np
import time

from src.schemas.layout import Layout
from src.schemas.output import Page
from services.base.model import BaseModelPrediction
from business.paddleocr3.utils.image import crop_img

from paddleocr import TableRecognitionPipelineV2

from src.logger import logger


class TablePrediction(BaseModelPrediction):
    def __init__(self, device: str = "cpu"):
        self.table_reco = TableRecognitionPipelineV2(
            device=device,
            use_ocr_model=True,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_layout_detection=True,
        )

    def batch_predict(self, images: list[Image.Image], pages: list[Page] = [], *args, **kwargs):
        current_pages: list[Page] = [Page(page=i) for i in range(len(images))]
        if len(pages):
            assert len(pages) == len(images)
            current_pages = pages

        logger.debug(f"[Table detection] nb image {len(images)}")

        for i in range(len(images)):
            image = images[i]
            layouts = current_pages[i].layouts.copy()
            logger.debug(f"[Table detection image {i}] nb layout {len(layouts)}")

            for layout in layouts:
                if layout.label == "table":
                    crop_image: Image.Image = crop_img(img=image, coordinates=layout.coordinate)
                    size = crop_image.size
                    crop_image = np.array(crop_image)
                    t = time.perf_counter()
                    table_cls = self.table_reco.predict(crop_image)
                    logger.debug(
                        f"[Table detection image {i} - {layout.label}] - crop size {size}  - time to process {time.perf_counter() - t:.2f}s"
                    )
                    for table in table_cls:
                        for layout_boxes, table_res in zip(table["layout_det_res"]["boxes"], table["table_res_list"]):
                            x0, y0, x1, y1 = layout_boxes["coordinate"]

                            x0 = layout.coordinate[0] * image.width + x0
                            x0 = x0 / image.width
                            y0 = layout.coordinate[1] * image.height + y0
                            y0 = y0 / image.height
                            x1 = layout.coordinate[2] * image.width + x1
                            x1 = x1 / image.width
                            y1 = layout.coordinate[3] * image.height + y1
                            y1 = y1 / image.height
                            tmp_lay = Layout(
                                cls_id=layout_boxes["cls_id"],
                                label=layout_boxes["label"],
                                score=layout_boxes["score"],
                                coordinate=[x0, y0, x1, y1],
                                content=table_res["pred_html"],
                            )
                            current_pages[i].layouts.append(tmp_lay)

        return current_pages
