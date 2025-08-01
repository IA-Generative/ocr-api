import asyncio
import logging
import instructor
import traceback
from openai import OpenAI, AsyncOpenAI

from business.llm.models.base import BaseLLMOCR
from src.utils.bboxes import sort_bboxes_reading_order, get_text_from_list_bboxes
from src.schemas.template import LLMFormField
from src.logger import logger

logger.setLevel(logging.DEBUG)


class FormFieldExtractor(BaseLLMOCR):
    def __init__(self, client: OpenAI | AsyncOpenAI, model_name: str):
        super().__init__(client, model_name, None)
        self.instructor = instructor.from_openai(self.client)
        self.delta_y: float = 0.005

    def batch_predict(self, images, pages=..., *args, **kwargs):
        for page in pages:
            try:
                sorted_bboxes = sort_bboxes_reading_order(bboxes=page.boxes, delta_y=self.delta_y)
                page_lines_content = []
                for line_sorted_boxes in sorted_bboxes:
                    text_line = get_text_from_list_bboxes(line_sorted_boxes)
                    page_lines_content.append(text_line)

                page_content = "\n".join(page_lines_content)
                prompt = f"""Voici le texte brut extrait par OCR. Pour chaque champ de type formulaire,
                            extrais key, value, puis propose corrected_key et corrected_value.
                            Inclus aussi les case qui sont cocher ou pas en value et en key correspondante de la case.
                            Dans le meme langue que le texte extrait.\n\n
                            {page_content}"""
                if isinstance(self.client, AsyncOpenAI):
                    result: list[LLMFormField] = asyncio.run(
                        self.instructor.chat.completions.create(
                            model=self.model_name,
                            response_model=list[LLMFormField],
                            messages=[{"role": "user", "content": prompt}],
                            max_retries=2,
                            temperature=0,
                        )
                    )
                else:
                    result: list[LLMFormField] = self.instructor.chat.completions.create(
                        model=self.model_name,
                        response_model=list[LLMFormField],
                        messages=[{"role": "user", "content": prompt}],
                        max_retries=2,
                        temperature=0,
                    )
                page.form_entries = result
            except Exception as e:
                logger.error(f"[model {self.__class__.__name__}] {str(e)}")
                logger.debug(traceback.format_exc())

        return pages
