import asyncio
from pathlib import Path
from io import BytesIO
import instructor
from PIL import Image
from openai import OpenAI, AsyncOpenAI
from typing import overload, Union
import base64
from src.schemas.template import LLMFormField
from src.schemas.output import Page
from business.llm.models.base import BaseLLMOCR


@overload
def encode_image(image_or_path: Path) -> str: ...


@overload
def encode_image(image_or_path: Image.Image) -> str: ...


def encode_image(image_or_path: Union[Image.Image, Path]) -> str:
    if isinstance(image_or_path, Image.Image):
        buffered = BytesIO()
        image_or_path.save(buffered, format="JPEG")  # ou PNG selon ton besoin
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    if isinstance(image_or_path, Path):
        return base64.b64encode(image_or_path.read_bytes()).decode("utf-8")
    raise NotImplementedError(f"{type(image_or_path)} is not avalable")


class LLMToForm(BaseLLMOCR):
    def __init__(
        self,
        client: OpenAI | AsyncOpenAI,
        model_name: str = "mistral-small-3.1-24b-instruct-2503",
    ):
        self.openai_client = client
        self.client = instructor.from_openai(self.openai_client)
        self.model_name = model_name
        self.prompt = "Extrais tous les champs du formulaire avec valeurs"
        self.batch_size = 2

    def process(self, image: Image.Image, batch_size: int = 2) -> list[LLMFormField]:
        b64 = encode_image(image_or_path=image)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,  # ou gpt‑4o selon ton accès
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                            },
                        ],
                    }
                ],
                max_tokens=1000,
                response_model=list[LLMFormField],
            )
        except Exception as e:
            response = []
            print(e)
        return response

    async def aprocess(self, image_or_path: Union[Image.Image, Path], batch_size: int = 2) -> list[LLMFormField]:
        semaphore = asyncio.Semaphore(batch_size)
        async with semaphore:
            b64 = encode_image(image_or_path=image_or_path)
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                            },
                        ],
                    }
                ],
                max_tokens=1000,
                response_model=list[LLMFormField],
            )
            return response

    async def _async_batch_predict(self, images: list[Image.Image], pages: list[Page]):
        semaphore = asyncio.Semaphore(self.batch_size)

        async def wrapped_aprocess(image):
            async with semaphore:
                return await self.aprocess(image)

        tasks = [wrapped_aprocess(image) for image in images]
        results = await asyncio.gather(*tasks)

        for page, result in zip(pages, results):
            page.form_entries = result

        return pages

    def batch_predict(self, images: list[Image.Image], pages: list[Page] = [], *args, **kwargs):
        if len(pages):
            if len(images) != len(pages):
                raise NotImplementedError("Please make suze same size")

        else:
            pages = [Page(page=i + 1) for i in range(len(images))]
        if isinstance(self.openai_client, OpenAI):
            for page, image in zip(pages, images):
                page.form_entries = self.process(image=image, batch_size=2)

            return pages

        return asyncio.run(self._async_batch_predict(images, pages))
