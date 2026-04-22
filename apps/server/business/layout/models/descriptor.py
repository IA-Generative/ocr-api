from src.schemas.layout import Layout
from src.schemas.layouts.image import ImageBlock
from src.schemas.layouts.formula import FormulaBlock
from src.schemas.layouts.table import TableBlock
from typing import Union
from services.base.model import BaseModelPrediction
from PIL import Image
from src.schemas.output import Page
import openai
import instructor
import base64
import io
from .prompts import (
    FORMULA_PROMPT,
    IMAGE_PROMPT,
    TABLE_PROMPT,
    formula_labels,
    image_labels,
    table_labels,
)
from src.config.openai import OpenAISettings
from src.logger import logger
import time

openai_settings = OpenAISettings()

TYPES = Union[FormulaBlock, ImageBlock, TableBlock]


class LayoutDescriptor(BaseModelPrediction):
    def __init__(
        self,
        client_openai: openai.OpenAI = openai.OpenAI(
            base_url=openai_settings.OPENAI_BASE_URL,
            api_key=openai_settings.OPENAI_API_KEY,
            timeout=openai_settings.OPENAI_TIMEOUT,
            max_retries=openai_settings.OPENAI_MAX_RETRIES,
        ),
        *args,
        **kwargs,
    ):
        # Initialize any necessary resources or configurations here
        self.client_openai = client_openai
        self.client_instructor = instructor.from_openai(client_openai, mode=instructor.Mode.MD_JSON)
        self.model_name = openai_settings.OPENAI_MODEL

    def select_prompt(self, label: str) -> str | None:
        if label in formula_labels:
            return FORMULA_PROMPT
        elif label in image_labels:
            return IMAGE_PROMPT
        elif label in table_labels:
            return TABLE_PROMPT
        else:
            return None

    def select_base_model(self, label: str) -> type[TYPES] | None:
        if label in formula_labels:
            return FormulaBlock
        elif label in image_labels:
            return ImageBlock
        elif label in table_labels:
            return TableBlock
        else:
            return None

    def build_messages(self, prompt: str, image_crop: Image.Image) -> list[dict]:
        buffer = io.BytesIO()
        image_crop.save(buffer, format="PNG")
        image_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                    },
                ],
            }
        ]
        return messages

    def batch_predict(self, images: list[Image.Image], pages: list = [], *args, **kwargs) -> list[Page]:
        # Placeholder implementation: returns empty layouts for each page
        if len(pages):
            assert len(images) == len(pages), "Number of images and pages must match"
        else:
            raise ValueError("Pages must be provided for layout prediction")
        if openai_settings.USE_DESCRIPTIOR:
            for i, image in enumerate(images):
                # width_img, height_img = image.size
                current_page: Page = pages[i]
                layouts: list[Layout] = current_page.layouts
                for layout in layouts:
                    prompt = self.select_prompt(layout.label)
                    model_cls = self.select_base_model(layout.label)
                    if prompt and model_cls:
                        xmin, ymin, xmax, ymax = layout.coordinate
                        # WARNING: the following cropping assumes is not normalized, if coordinates are normalized, they should be denormalized before cropping
                        cropped_image = image.crop((xmin, ymin, xmax, ymax))
                        try:
                            messages = self.build_messages(prompt, cropped_image)
                            t0 = time.time()
                            logger.info(
                                f"Sending layout descriptor request for page {current_page.page}, layout label: {layout.label}"
                            )
                            response: model_cls = self.client_instructor.create(
                                model=self.model_name,
                                messages=messages,
                                response_model=model_cls,
                            )  # ty:ignore[no-matching-overload]
                            layout.block = response
                            logger.info(
                                f"Received layout descriptor response for page {current_page.page} in {time.time() - t0:.2f}s: {response}"
                            )
                        except Exception as e:
                            logger.error(f"Error processing layout descriptor for page {current_page.page}: {e}")
                            continue
        else:
            logger.info("Skipping layout description as USE_DESCRIPTOR is set to False")

        return pages
