from typing import Optional
from pydantic import BaseModel


class EvaluationMetrics(BaseModel):
    id: Optional[str] = None
    expected: str
    predicted: str
    inference_time: float
    iou: float
    cer: float
    wer: float
    dataset_name: str
    page_num: int
    model_name: str
    recall: float = 0.0
    precision: float = 0.0
    f1: float = 0.0
    source: str
