import json
from evaluation.eval_recognition.schema import EvaluationMetrics
import hashlib


class BaseModelMonitoring:
    def __init__(self):
        pass

    def send(self, data: EvaluationMetrics):
        raise NotImplementedError("La méthode 'send' n'est pas implémentée.")


class JsonModelMonitoring(BaseModelMonitoring):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename

    def send(self, data: EvaluationMetrics):
        data.id = hashlib.sha256((data.source + f"{data.page_num}").encode()).hexdigest()
        with open(self.filename, "a") as f:
            f.write(f"{json.dumps(data.model_dump())}\n")
