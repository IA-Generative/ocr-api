from typing import Union
import uuid
import os

from src.schemas.output import Page, Bbox
from src.schemas.task import TaskModel
from src.logger import logger
from business.extractions.models.inference import FileExtractionModel

CSV_CONTENT_TYPE = ["text/csv"]


class CSVExtractionModel(FileExtractionModel):
    def __init__(self):
        from langchain_community.document_loaders import CSVLoader

        self.loader = CSVLoader

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type in CSV_CONTENT_TYPE

    def batch_predict(
        self,
        images: list[Union[bytes, str]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []

        for i, image in enumerate(images):
            with open(f"/tmp/{uuid.uuid4()}.csv", "wb") as temp_file:
                temp_file.write(image)
                temp_file_path = temp_file.name

            try:
                logger.debug(f"[CSVExtractionModel] Processing file {temp_file_path}")
                loader_instance = self.loader(file_path=temp_file_path)
                documents = loader_instance.load()
                text_content = "\n".join([doc.page_content for doc in documents])
                logger.debug(f"[CSVExtractionModel] Extracted text content: {text_content[:100]}...")

                page = Page(
                    page=i + 1,
                    boxes=[
                        Bbox(
                            x=0,
                            y=0,
                            width=1,
                            height=1,
                            text=text_content,
                            confidence=1.0,
                        )
                    ],
                )
                result.append(page)
            except Exception as e:
                logger.error(f"[CSVExtractionModel] Error processing file {image}: {e}")
                page = Page(
                    page=i + 1,
                    boxes=[],
                )
                result.append(page)

            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        return result
