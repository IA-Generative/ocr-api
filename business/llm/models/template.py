import instructor

from business.llm.models.base import BaseLLMOCR
from src.utils.bboxes import sort_bboxes_reading_order, get_text_from_list_bboxes
from src.schemas.template import FormExtraction


class TemplateLLMDetector(BaseLLMOCR):
    def __init__(self, client, model_name):
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
                result: FormExtraction = self.instructor.chat.completions.create(
                    model=self.model_name,
                    response_model=FormExtraction,
                    messages=[{"role": "user", "content": prompt}],
                    max_retries=2,
                    temperature=0,
                )
                page.form_entries = result.entries
            except Exception as e:
                print(e)

        return pages
