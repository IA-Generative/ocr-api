from typing import Union
from uuid import uuid4
import os
import pandas as pd

from src.schemas.output import Page, Bbox
from src.schemas.task import TaskModel
from src.logger import logger
from business.extractions.models.inference import FileExtractionModel

EXCEL_CONTENT_TYPE = [
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/xlsx",
    "application/xls",
    "application/x-xlsx",
    "application/x-xls",
    "application/x-excel",
    "application/x-msexcel",
]


class ExcelExtractionModel(FileExtractionModel):
    def __init__(self):
        pass

    def is_applicable(self, task: TaskModel) -> bool:
        return task.input.content_type in EXCEL_CONTENT_TYPE

    def _get_file_extension(self, content_type: str) -> str:
        """Détermine l'extension du fichier basée sur le content-type"""
        if content_type in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/xlsx",
            "application/x-xlsx",
        ]:
            return ".xlsx"
        else:
            return ".xls"

    def batch_predict(
        self,
        images: list[Union[bytes, str]],
        pages: list[Page] = [],
        task: TaskModel = None,
        *args,
        **kwargs,
    ) -> list[Page]:
        result: list[Page] = []

        for i, image in enumerate(images):
            # Détermine l'extension correcte basée sur le content-type
            file_ext = ".xlsx"  # par défaut
            if task and hasattr(task, "input"):
                file_ext = self._get_file_extension(task.input.content_type)

            temp_file_path = f"/tmp/{uuid4()}{file_ext}"

            try:
                with open(temp_file_path, "wb") as temp_file:
                    temp_file.write(image)

                # Utilise pandas pour lire le fichier Excel
                if file_ext == ".xlsx":
                    # Pour les fichiers .xlsx
                    excel_data = pd.read_excel(temp_file_path, sheet_name=None, engine="openpyxl")
                else:
                    # Pour les fichiers .xls
                    excel_data = pd.read_excel(temp_file_path, sheet_name=None, engine="xlrd")

                text_content = ""

                # Traite chaque feuille
                for sheet_name, df in excel_data.items():
                    if not df.empty:
                        text_content += f"=== {sheet_name} ===\n"
                        # Convertit le DataFrame en texte tabulé
                        text_content += df.to_string(index=False, na_rep="") + "\n\n"

                page = Page(
                    page=i + 1,
                    boxes=[
                        Bbox(
                            x=0,
                            y=0,
                            width=1,
                            height=1,
                            text=text_content.strip(),
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
