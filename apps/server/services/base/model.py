from abc import ABC, abstractmethod
from typing import Union
import numpy as np
from PIL import Image
from src.schemas.output import Page


class BaseModelPrediction(ABC):
    @abstractmethod
    def batch_predict(
        self,
        images: list[Union[np.ndarray, Image.Image]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]: ...
