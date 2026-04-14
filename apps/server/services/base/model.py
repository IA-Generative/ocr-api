from abc import ABC, abstractmethod
from typing import Union
import numpy as np
from PIL import Image
from src.schemas.output import Page
from src.schemas.task import TaskModel


class BaseModelPrediction(ABC):
    def __init__(self):
        self.current_task: TaskModel | None = None

    def set_current_task(self, task: TaskModel):
        self.current_task = task

    @abstractmethod
    def batch_predict(
        self,
        images: list[Union[np.ndarray, Image.Image, bytes]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]: ...
