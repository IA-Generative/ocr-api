# CREDITS: https://github.com/Manikandan-Thangaraj-ZS0321/checkbox_detection_opencv/blob/master/checkbox_detection_classification.py

import cv2
import numpy as np


from time import time
from PIL import Image
from src.schemas.box import Checkbox
from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.logger import logger


def detect_checkboxes(image, line_min_width=15, line_max_width=15):
    gray_scale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, img_bin = cv2.threshold(gray_scale, 150, 255, cv2.THRESH_BINARY)
    img_bin = ~img_bin

    kernal_h_min = np.ones((1, line_min_width), np.uint8)
    kernal_v_min = np.ones((line_min_width, 1), np.uint8)
    kernal_h_max = np.ones((1, line_max_width), np.uint8)
    kernal_v_max = np.ones((line_max_width, 1), np.uint8)

    # Apply morphological operations
    img_bin_h_min = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_h_min)
    img_bin_v_min = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernal_v_min)
    img_bin_h_max = cv2.morphologyEx(img_bin, cv2.MORPH_CLOSE, kernal_h_max)
    img_bin_v_max = cv2.morphologyEx(img_bin, cv2.MORPH_CLOSE, kernal_v_max)

    # Combine the results
    img_bin_final = (img_bin_h_min & img_bin_h_max) | (img_bin_v_min & img_bin_v_max)

    final_kernel = np.ones((3, 3), np.uint8)
    img_bin_final = cv2.dilate(img_bin_final, final_kernel, iterations=1)

    # Find connected components
    _, labels, stats, _ = cv2.connectedComponentsWithStats(~img_bin_final, connectivity=8, ltype=cv2.CV_32S)

    return stats, labels


def classify_checkboxes(
    image: Image.Image,
    img_width: int,
    img_height: int,
    stats,
    min_width: int = 10,
    max_width: int = 50,
    tick_threshold: float = 0.1,
) -> list[Checkbox]:
    checkboxes = []
    for stat in stats[2:]:
        x, y, w, h, _ = stat
        aspect_ratio = w / h
        if min_width <= w <= max_width and min_width <= h <= max_width and 0.8 <= aspect_ratio <= 1.2:
            roi = image[y : y + h, x : x + w]
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray_roi = cv2.GaussianBlur(gray_roi, (5, 5), 0)
            binary_roi = cv2.adaptiveThreshold(
                gray_roi,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                11,
                2,
            )
            kernel = np.ones((3, 3), np.uint8)
            binary_roi = cv2.morphologyEx(binary_roi, cv2.MORPH_OPEN, kernel)

            non_white_pixels = cv2.countNonZero(binary_roi)
            total_pixels = w * h
            tick_percentage = non_white_pixels / total_pixels
            is_checked = False

            if tick_percentage > tick_threshold:
                is_checked = True

            checkbox_model = Checkbox(
                x=x / img_width,
                y=y / img_height,
                width=w / img_width,
                height=h / img_height,
                is_checked=is_checked,
                confidence=tick_percentage,
            )
            checkboxes.append(checkbox_model)

    return checkboxes


class MorphoBoxDetection(BaseModelPrediction):
    def __init__(self):
        super().__init__()

    def batch_predict(self, images: list[Image.Image], pages: list[Page] = [], *args, **kwargs):
        current_pages: list[Page] = [Page(page=i) for i in range(len(images))]
        if len(pages):
            assert len(pages) == len(images), "Not the same lenght"
            current_pages = pages

        for image, page in zip(images, current_pages):
            t = time()
            image = image.convert("RGB")
            img_width, img_height = image.size
            image = np.array(image)
            stats, _ = detect_checkboxes(image)
            checkboxes = classify_checkboxes(image, img_height=img_height, img_width=img_width, stats=stats)
            logger.debug(f"[MorphoCheckboxes] time : {time()-t:.2f}s")
            page.checkboxes = checkboxes

        return current_pages
