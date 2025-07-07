import logging
import base64
from io import BytesIO
from PIL import Image
from services.base.model import BaseModelPrediction
from src.logger import logger
from openai import OpenAI
from src.schemas.output import Page
from src.schemas.layout import Layout
from src.schemas.box import Bbox


logger.setLevel(logging.DEBUG)


def pil_image_to_base64(pil_img: Image.Image, img_format: str = "JPEG") -> str:
    """
    Convertit une image PIL en chaîne Base64.

    Args:
        pil_img: instance de PIL.Image.Image
        img_format: format de sortie, ex. "JPEG", "PNG"

    Retour:
        str: image encodée en Base64 (utf-8)
    """
    buffered = BytesIO()
    pil_img.save(buffered, format=img_format)
    img_bytes = buffered.getvalue()
    base64_bytes = base64.b64encode(img_bytes)
    return base64_bytes.decode("utf-8")


class BaseLLMOCR(BaseModelPrediction):
    def __init__(self, client: OpenAI, model_name: str, prompt: str):
        self.client = client
        self.model_name = model_name
        self.prompt = prompt


class VisionLLMOCR(BaseLLMOCR):
    def __init__(self, client: OpenAI, model_name: str):
        prompt = """Tu es un assistant OCR.
            Ta mission : extrais **strictement** tout le texte visible **tel quel**,
            sans reformuler, sans résumer, sans ajouter quoi que ce soit.
            Conserve la ponctuation, les sauts de ligne et la mise en page d’origine.
            Sous format markddown
            """
        super().__init__(client, model_name=model_name, prompt=prompt)

    def batch_predict(self, images, pages: list[Page] = [], *args, **kwargs):
        if len(pages):
            assert len(pages) == len(images)
        else:
            pages = [Page(page=i) for i in range(len(images))]
        for image, page in zip(images, pages):
            base64_image = pil_image_to_base64(image)
            response = self.client.responses.create(
                model=self.model_name,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": self.prompt},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        ],
                    }
                ],
            )

            tmp_lay = Layout(
                cls_id=-1,
                label="llm",
                score=-1,
                coordinate=[0, 0, 1, 1],
                content=response.output_text,
            )
            page.layouts.append(tmp_lay)
            page.boxes.append(Bbox(x=0, y=0, width=1, height=1, confidence=-1, text=tmp_lay.content))
        return pages
