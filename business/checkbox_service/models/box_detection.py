from typing import Union
import logging
from time import time
import numpy as np
from PIL import Image
from boxdetect import config
from src.schemas.box import Checkbox
from boxdetect.pipelines import get_checkboxes
from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.logger import logger

logger.setLevel(logging.DEBUG)

cfg = config.PipelinesConfig()

# important to adjust these values to match the size of boxes on your image
cfg.width_range = (30, 55)
cfg.height_range = (25, 40)

# the more scaling factors the more accurate the results but also it takes more time to processing
# too small scaling factor may cause false positives
# too big scaling factor will take a lot of processing time
cfg.scaling_factors = [0.7, 1.0]

# w/h ratio range for boxes/rectangles filtering
cfg.wh_ratio_range = (0.5, 1.7)

# group_size_range starting from 2 will skip all the groups
# with a single box detected inside (like checkboxes)
cfg.group_size_range = (2, 100)

# num of iterations when running dilation tranformation (to engance the image)
cfg.dilation_iterations = 0


class BoxDetection(BaseModelPrediction):
    def __init__(self, cfg: config.PipelinesConfig = cfg):
        self.cfg = cfg
        self.px_threshold = 0.2

    def batch_predict(
        self,
        images: list[Union[np.ndarray, Image.Image]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        current_pages: list[Page] = [Page(page=i) for i in range(len(images))]
        if len(pages):
            assert len(pages) == len(images), "Not the same lenght"
            current_pages = pages

        for image, page in zip(images, current_pages):
            t = time()
            image = image.convert("RGB")
            img_width, img_height = image.size
            image = np.array(image)
            checkboxes = get_checkboxes(img=image, cfg=self.cfg, verbose=False, px_threshold=self.px_threshold)
            logger.debug(f"[Checkboxes] time : {time()-t:.2f}s")
            page_checkboxes: list[Checkbox] = []

            for checkbox in checkboxes:
                bbox, is_checked, crop_img = checkbox
                x, y, width, height = bbox
                all_px_count = crop_img.shape[0] * crop_img.shape[1]
                nonzero_px_count = np.count_nonzero(crop_img)
                checkbox_model = Checkbox(
                    x=x / img_width,
                    y=y / img_height,
                    width=width / img_width,
                    height=height / img_height,
                    is_checked=is_checked,
                    confidence=nonzero_px_count / all_px_count,
                )
                page_checkboxes.append(checkbox_model)
                page.boxes.append(
                    Bbox(
                        x=checkbox_model.x,
                        y=checkbox_model.y,
                        width=checkbox_model.width,
                        height=checkbox_model.height,
                        confidence=nonzero_px_count / all_px_count,
                        text="[x]" if is_checked else "[ ]",
                    )
                )

            page.checkboxes = page_checkboxes

        return current_pages
