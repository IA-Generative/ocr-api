from typing import Union
from uuid import uuid4
import os
from src.schemas.task import TaskModel
from src.schemas.output import Page, Bbox
from src.logger import logger


from business.extractions.models.inference import FileExtractionModel

PPTX_CONTENT_TYPE = [
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/mspowerpoint",
    "application/powerpoint",
    "application/vnd.ms-powerpoint",
    "application/x-mspowerpoint",
]
# TODO: WARNING: currently not working due to unstructured lib issue
class PPTXExtractionModel(FileExtractionModel):
    def __init__(self):
        from langchain_community.document_loaders import UnstructuredPowerPointLoader

        self.loader = UnstructuredPowerPointLoader

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type in PPTX_CONTENT_TYPE

    def batch_predict(
        self,
        images: list[Union[bytes, str]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []

        for i, image in enumerate(images):
            with open(f"/tmp/{uuid4()}.ppt", "wb") as temp_file:
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
                logger.error(f"[{self.__class__.__name__}] Error processing file: {e}")
                page = Page(
                    page=i + 1,
                    text="",
                    boxes=[],
                )
                result.append(page)
            finally:
                os.remove(temp_file_path)

        return result
