from abc import ABC, abstractmethod
from typing import Union, Any
import numpy as np
from PIL import Image


class BaseModelPrediction(ABC):
    @abstractmethod
    def batch_predict(
        self, images: list[Union[np.ndarray, Image.Image]], *args, **kwargs) -> Any: ...
