from typing import Union
import os
from uuid import uuid4

from src.schemas.output import Page, Bbox
from src.schemas.task import TaskModel
from src.logger import logger

from business.extractions.models.inference import FileExtractionModel

ODT_CONTENT_TYPE = ["application/vnd.oasis.opendocument.text"]
ODS_CONTENT_TYPE = ["application/vnd.oasis.opendocument.spreadsheet"]
ODP_CONTENT_TYPE = ["application/vnd.oasis.opendocument.presentation"]


class ODTExtractionModel(FileExtractionModel):
    def __init__(self):
        from langchain_community.document_loaders import UnstructuredODTLoader

        self.loader = UnstructuredODTLoader

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type in ODT_CONTENT_TYPE

    def batch_predict(
        self,
        images: list[Union[bytes, str]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []

        for i, image in enumerate(images):
            with open(f"/tmp/{uuid4()}.odt", "wb") as temp_file:
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
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        return result


class OdsExtractionModel(FileExtractionModel):
    def __init__(self):
        try:
            from odf.opendocument import load
            from odf.table import Table, TableRow, TableCell
            from odf.text import P

            self.odf_load = load
            self.Table = Table
            self.TableRow = TableRow
            self.TableCell = TableCell
            self.P = P
        except ImportError:
            logger.warning("odfpy not installed. Please install it: pip install odfpy")
            self.odf_load = None

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type in ODS_CONTENT_TYPE

    def batch_predict(
        self,
        images: list[Union[bytes, str]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []

        for i, image in enumerate(images):
            with open(f"/tmp/{uuid4()}.ods", "wb") as temp_file:
                temp_file.write(image)
                temp_file_path = temp_file.name
            try:
                if self.odf_load is None:
                    raise ImportError("odfpy not available")

                doc = self.odf_load(temp_file_path)
                text_content = ""

                # Extract text from tables
                for table in doc.getElementsByType(self.Table):
                    for row in table.getElementsByType(self.TableRow):
                        row_text = []
                        for cell in row.getElementsByType(self.TableCell):
                            cell_text = ""
                            for p in cell.getElementsByType(self.P):
                                cell_text += str(p)
                            row_text.append(cell_text)
                        text_content += "\t".join(row_text) + "\n"

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
                    boxes=[],
                )
                result.append(page)
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        return result


class OdpExtractionModel(FileExtractionModel):
    def __init__(self):
        try:
            from odf.opendocument import load
            from odf.text import P
            from odf.draw import Page as DrawPage

            self.odf_load = load
            self.P = P
            self.DrawPage = DrawPage
        except ImportError:
            logger.warning("odfpy not installed. Please install it: pip install odfpy")
            self.odf_load = None

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type in ODP_CONTENT_TYPE

    def batch_predict(
        self,
        images: list[Union[bytes, str]],
        pages: list[Page] = [],
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []

        for i, image in enumerate(images):
            with open(f"/tmp/{uuid4()}.odp", "wb") as temp_file:
                temp_file.write(image)
                temp_file_path = temp_file.name
            try:
                if self.odf_load is None:
                    raise ImportError("odfpy not available")

                doc = self.odf_load(temp_file_path)
                text_content = ""

                # Extract text from presentation slides
                for draw_page in doc.getElementsByType(self.DrawPage):
                    for p in draw_page.getElementsByType(self.P):
                        text_content += str(p) + "\n"

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
                    boxes=[],
                )
                result.append(page)
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

        return result
