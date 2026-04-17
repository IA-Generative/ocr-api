from PIL import Image

import openai
from openai.types.responses.parsed_response import ParsedResponse

from services.base.model import BaseModelPrediction
from src.schemas.output import Page
from src.logger import logger
from src.schemas.classification import (
    ClassificationResult,
    LabelDefinition,
    Model,
    BatchPredictionsOutput,
)
from business.paddleocr2.configs.classification import ClassificationSettings

settings = ClassificationSettings()


class TextClassificationModel(BaseModelPrediction):
    def __init__(
        self,
        client: openai.OpenAI,
        model_name: str = settings.MODEL_NAME,
    ):
        # Charger modèle
        self.model_name = model_name
        self.model_definition = Model(name=model_name, version="1.0")
        self.labels: list[LabelDefinition] | None = None
        self.batch_page_size = 2
        self.batch_classification_size = 5
        self.client = client
        self.prompt = (
            "You are a helpful assistant for classifying text content of document pages. "
            "Given the text content of a page and a list of possible labels with their definitions, "
            "you will assign the most relevant labels to the page based on its content. "
            "The output should be a list of labels that best describe the content of the page. "
            "{labels} is the list of possible labels with their definitions."
        )

    def set_labels(self, labels: list[LabelDefinition]):
        self.labels = labels

    def batch_predict(
        self,
        images: list[Image.Image],
        pages: list = [],
        labels: list[LabelDefinition] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        label_mapper = {label.label: label for label in labels}
        if len(pages):
            assert len(images) == len(pages), "Number of images and pages must match"
        if len(labels):
            self.set_labels(labels)
        else:
            raise ValueError("No labels provided for classification.")

        if not self.labels:
            logger.warning("No labels provided for classification. Skipping classification step.")
            return pages  # Pas de classification possible sans labels

        for batch_page_index in range(0, len(pages), self.batch_page_size):
            pages_batch = pages[batch_page_index : batch_page_index + self.batch_page_size]

            page_indices = range(batch_page_index, batch_page_index + self.batch_page_size)

            page_text = [f"Page {page_number}: {page.text}" for page_number, page in zip(page_indices, pages_batch)]
            for batch_label_index in range(0, len(labels), self.batch_classification_size):
                batch_label = labels[batch_label_index : batch_label_index + self.batch_classification_size]
                batch_label_str = ", ".join([f"{label.label} ({label.definition})" for label in batch_label])

                result: ParsedResponse[BatchPredictionsOutput] = self.client.responses.parse(
                    model=self.model_name,
                    input=[
                        {
                            "role": "system",
                            "content": self.prompt.format(labels=batch_label_str),
                        },
                        {
                            "role": "user",
                            "content": "\n".join(page_text),
                        },
                    ],
                    text_format=BatchPredictionsOutput,
                )
                if not result.output_parsed or not result.output_parsed.predictions:
                    logger.warning(
                        f"Model did not return valid predictions for batch starting at page index {batch_page_index} with labels batch starting at index {batch_label_index}."
                    )
                    continue
                for page_result in result.output_parsed.predictions:
                    page_index = page_result.page_number
                    predicted_labels = page_result.predictions
                    if page_index < len(pages):
                        pages[page_index].classification = [
                            ClassificationResult(
                                label=label_mapper.get(
                                    pred.label,
                                    LabelDefinition(label=pred.label, definition=""),
                                ),
                                confidence=pred.confidence,
                                model=self.model_definition,
                            )
                            for pred in predicted_labels
                        ]

        return pages
