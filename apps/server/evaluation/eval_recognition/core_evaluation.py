from PIL.Image import Image
from services.base.model import BaseModelPrediction
from tqdm import tqdm

from evaluation.eval_recognition.schema import EvaluationMetrics
from evaluation.eval_recognition.metrics import (
    set_text,
    cer,
    wer,
    iou_text,
    precision,
    recall,
    f1_score,
)

from evaluation.eval_recognition.data import (
    PixParseDataset,
)

from langfuse import Langfuse
from langfuse.api.resources.commons.types import DatasetRunItem


class BaseEvaluation:
    def process(self):
        raise NotImplementedError("La méthode 'process' n'est pas implémentée.")


class Evaluation(BaseEvaluation):
    def __init__(
        self,
        model: BaseModelPrediction,
        dataset: PixParseDataset,
        langfuse: Langfuse = None,
        run_name: str = "ocr-evaluation",
    ):
        self.model = model
        self.dataset = dataset
        self.langfuse = langfuse
        self.langfuse_dataset = self.langfuse.get_dataset(self.dataset.dataset_name)
        self.run_name = run_name

    def update_dataset(self):
        self.langfuse_dataset = self.langfuse.get_dataset(self.dataset.dataset_name)

    def process(self):
        counter = 0
        for item in self.dataset:
            sources, texts, images = item
            for page_num, (source, text, image) in tqdm(enumerate(zip(sources, texts, images))):
                image: Image = image

                self.update_dataset()
                lang_data: DatasetRunItem = self.langfuse_dataset.items[counter]
                counter += 1

                with lang_data.run(run_name=self.run_name) as root_span:
                    pages = self.model.batch_predict(images=[image])

                    predict = set_text(pages[0])
                    root_span.update_trace(
                        input={
                            "page_number": page_num,
                            "source": source,
                            "image_size": image.size,
                        },
                        output={"text": predict},
                        metadata={
                            "dataset_name": self.dataset.dataset_name,
                            "model_name": self.model.__class__.__name__,
                        },
                    )
                    data = EvaluationMetrics(
                        expected="text",
                        predicted=predict,
                        cer=cer(text, predict),
                        wer=wer(text, predict),
                        iou=iou_text(text, predict),
                        precision=precision(text, predict),
                        recall=recall(text, predict),
                        f1=f1_score(text, predict),
                        inference_time=0,
                        dataset_name=self.dataset.dataset_name,
                        page_num=page_num,
                        model_name=self.model.__class__.__name__,
                        source=source,
                    )

                    root_span.score_trace(
                        name="cer",
                        value=data.cer,
                        data_type="NUMERIC",
                        comment="Character Error Rate",
                    )

                    root_span.score_trace(
                        name="wer",
                        value=data.wer,
                        data_type="NUMERIC",
                        comment="Word Error Rate",
                    )
                    root_span.score_trace(
                        name="recall",
                        value=data.recall,
                        data_type="NUMERIC",
                        comment="Recall",
                    )
                    root_span.score_trace(
                        name="precision",
                        value=data.precision,
                        data_type="NUMERIC",
                        comment="Precision",
                    )
                    root_span.score_trace(
                        name="f1_score",
                        value=data.f1,
                        data_type="NUMERIC",
                        comment="F1 Score",
                    )
