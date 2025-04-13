import time
import numpy as np

from src.logger import logger
from .fast_paddle import ppocr_v3
from ..utils.paddle import parse_paddle_ocr_result


def perform_ocr_async(img_array: np.ndarray):
    t = time.time()
    logger.info(f"image shpe {img_array.shape}")
    if len(img_array.shape) == 4:
        result_ocr = ppocr_v3.batch_predict(img_array)
        logger.debug(f"time to procces image : {time.time() - t}s")
        return [parse_paddle_ocr_result(res) for res in result_ocr]
    result_ocr = ppocr_v3.predict(img_array)
    return [parse_paddle_ocr_result(result_ocr)]
