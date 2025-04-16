
from typing import List
from PIL import Image
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor
from surya.recognition.schema import OCRResult
import torch
from ocr_service.models.base import BaseModelPrediction
from src.schemas.prediction import PredictionOCR


class SuryaOCR(BaseModelPrediction):
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu",
                 checkpoint_detection: str = None,
                 checkpoint_recognition: str = None):
        self.detection_predictor = DetectionPredictor(
            checkpoint=checkpoint_detection, device=device)
        self.recognition_predictor = RecognitionPredictor(
            checkpoint=checkpoint_recognition, device=device)

    def batch_predict(self, images: List[Image.Image], langs: List[List[str]] = [['fr']], detection_batch_size=1, recognition_batch_size=4) -> List[List[PredictionOCR]]:
        predictions: List[OCRResult] = self.recognition_predictor(
            images, langs=langs, det_predictor=self.detection_predictor, detection_batch_size=detection_batch_size, recognition_batch_size=recognition_batch_size)

        result: List[List[PredictionOCR]] = []
        for page_pred in predictions:
            page_predictions: List[PredictionOCR] = []
            for text_pred in page_pred.text_lines:
                tmp = PredictionOCR(confidence=text_pred.confidence,
                                    text=text_pred.text, text_region=text_pred.bbox)
                page_predictions.append(tmp)
            result.append(page_predictions)

        return result
