from abc import ABC, abstractmethod
from io import BytesIO
from typing import Union, Any
import numpy as np
from PIL import Image


class BaseModelPrediction(ABC):
    @abstractmethod
    def batch_predict(
        self, images_or_bytes_io: list[Image.Image | BytesIO], *args, **kwargs
    ) -> Any: ...
