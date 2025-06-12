from abc import ABC, abstractmethod
from typing import List
from PIL import Image

from paddleocr import FormulaRecognition

import numpy as np

from src.schemas.box import PredictText


class BaseFormulaModel(ABC):
    @abstractmethod
    def predict(self, images: list[Image.Image]) -> List[PredictText]: ...


class PaddleFormulaPredcition(BaseFormulaModel):
    def __init__(
        self,
        model_name: str = "PP-FormulaNet_plus-M",
        device: str = "cpu",
        batch_size: int = 1,
    ):
        self.model = FormulaRecognition(model_name=model_name, device=device)
        self.batch_size = batch_size

    def predict(self, images: list[Image.Image]) -> List[PredictText]:
        result = self.model.predict(
            [np.array(image.convert("RGB")) for image in images],
            batch_size=self.batch_size,
        )
        formulas = []
        for res in result:
            formulas.append(PredictText(text=res["rec_formula"], confidence=1))

        return formulas
