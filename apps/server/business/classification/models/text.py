import openai
from openai.types.responses.parsed_response import ParsedResponse

from src.schemas.output import Page
from src.logger import logger
from src.schemas.task import TaskModel
from src.schemas.classification import (
    ClassificationResult,
    LabelDefinition,
    Model,
    BatchPredictionsOutput,
)
from src.config.openai import OpenAISettings
from src.utils.bboxes import sort_bboxes_reading_order, get_text_from_list_bboxes
from src.schemas.classification import ParameterClassification
from services.client.tools import server_client
from src.schemas.task import TaskStatus

settings = OpenAISettings()


def set_page_text(page: Page, delta_y: float = 0.005) -> str:
    page_lines_content = []

    sorted_bboxes = sort_bboxes_reading_order(bboxes=page.boxes, delta_y=delta_y)
    for line_sorted_boxes in sorted_bboxes:
        text_line = get_text_from_list_bboxes(line_sorted_boxes)
        page_lines_content.append(text_line)

    page_content = "\n".join(page_lines_content)
    return page_content


class TextClassificationModel:
    def __init__(
        self,
        client: openai.OpenAI = openai.OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL),
        model_name: str = settings.OPENAI_MODEL,
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

    def query_llm(self, page_text: str, labels: list[LabelDefinition]) -> ParsedResponse[BatchPredictionsOutput]:
        batch_label_str = ", ".join([f"{label.label} ({label.definition})" for label in labels])

        result: ParsedResponse[BatchPredictionsOutput] = self.client.responses.parse(
            model=self.model_name,
            input=[
                {
                    "role": "system",
                    "content": self.prompt.format(labels=batch_label_str),
                },
                {
                    "role": "user",
                    "content": page_text,
                },
            ],
            text_format=BatchPredictionsOutput,
        )
        return result

    def process(
        self,
        task: TaskModel,
        *args,
        **kwargs,
    ) -> TaskModel:

        server_client.update_task_by_id(
            task_id=task.id,
            task_type=task.type,
            update_data={"status": TaskStatus.IN_PROGRESS.value, "percentage": 0.0},
        )

        parameters = task.parameters
        if not parameters:
            raise ValueError("Task parameters are required for classification.")

        parameters = ParameterClassification.model_validate(parameters)

        labels = parameters.labels if parameters and parameters.labels else []
        if not labels:
            raise ValueError("No labels provided for classification.")

        label_mapper = {label.label: label for label in labels}
        if not task.output or not task.output.pages:
            raise ValueError("Task output with pages is required for classification.")

        for batch_page_index in range(0, len(task.output.pages), self.batch_page_size):
            pages_batch: list[Page] = task.output.pages[batch_page_index : batch_page_index + self.batch_page_size]

            page_indices = range(batch_page_index, batch_page_index + self.batch_page_size)

            page_text = [
                f"Page {page_number}: {set_page_text(page)}" for page_number, page in zip(page_indices, pages_batch)
            ]
            for batch_label_index in range(0, len(labels), self.batch_classification_size):
                batch_label = labels[batch_label_index : batch_label_index + self.batch_classification_size]

                result: ParsedResponse[BatchPredictionsOutput] = self.query_llm(
                    page_text="\n".join(page_text),
                    labels=batch_label,
                )
                if not result.output_parsed or not result.output_parsed.predictions:
                    logger.warning(
                        f"Model did not return valid predictions for batch starting at page index {batch_page_index} with labels batch starting at index {batch_label_index}."
                    )
                    continue
                for page_result in result.output_parsed.predictions:
                    page_index = page_result.page_number
                    predicted_labels = page_result.predictions
                    if page_index < len(task.output.pages):
                        task.output.pages[page_index].classifications = [
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
            server_client.update_task_by_id(
                task_id=task.id,
                task_type=task.type,
                update_data={
                    "status": TaskStatus.IN_PROGRESS.value,
                    "percentage": min(
                        0.99,
                        (batch_page_index + self.batch_page_size) / len(task.output.pages),
                    ),
                },
            )
        logger.info(f"Classification completed for {len(task.output.pages)} pages.")
        logger.debug(79 * "-")
        return task
