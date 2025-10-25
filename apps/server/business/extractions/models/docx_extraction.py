from business.extractions.models.inference import FileExtractionModel
from typing import Union
from uuid import uuid4
import os


from src.schemas.output import Page, Bbox
from src.schemas.task import TaskModel
from src.logger import logger

DOCX_CONTENT_TYPE = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/docx",
    "application/msword",
    "application/x-docx",
    "application/doc",
    "application/ms-doc",
]


class DocxExtractionModel(FileExtractionModel):
    def __init__(self):
        from langchain_community.document_loaders import Docx2txtLoader

        self.loader = Docx2txtLoader

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type in DOCX_CONTENT_TYPE

    def batch_predict(
        self,
        images: list[Union[bytes, str]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []

        for i, image in enumerate(images):
            with open(f"/tmp/{uuid4()}.docx", "wb") as temp_file:
                temp_file.write(image)
                temp_file_path = temp_file.name
            try:
                loader_instance = self.loader(file_path=temp_file_path)
                documents = loader_instance.load()
                text_content = "\n".join([doc.page_content for doc in documents])

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
                logger.error(f"[{self.__class__.__name__}] Error processing file : {e}")
                page = Page(
                    page=i + 1,
                    text="",
                    boxes=[],
                )
                result.append(page)
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        return result
