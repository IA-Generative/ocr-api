import os 
from typing import List
from PIL import Image
from ocr_service.models.base import BaseModelPrediction
from src.schemas.prediction import PredictionOCR
from paddleocr import PaddleOCR
import numpy as np

class PaddleInferOCR(BaseModelPrediction):
    def __init__(self, path_model : str):
        self.model: PaddleOCR = PaddleOCR(
            det_model_dir=os.path.join(path_model,  "detection"),
            rec_model_dir=os.path.join(path_model, "recognition"),
            cls_model_dir=os.path.join(path_model, "classification"),
            use_angle_cls=False,
            lang="fr",
        )

    def batch_predict(self, images: List[Image.Image], *args, **kwargs) -> List[List[PredictionOCR]]:
        result: List[List[PredictionOCR]] = []
        for image in images:
            predictions = self.model.ocr(np.array(image), det=True, rec=True, cls=True)
            for pred in predictions:
                page_predictions: List[PredictionOCR] = []
                for text_pred in pred:
                    bbox, (text, confidence) = text_pred
                    prediction_bbox = []
                    for xy in bbox:
                        prediction_bbox.extend(xy)
                    tmp = PredictionOCR(confidence=confidence,
                                        text=text, text_region=prediction_bbox)
                    page_predictions.append(tmp)
                result.append(page_predictions)

        return result
