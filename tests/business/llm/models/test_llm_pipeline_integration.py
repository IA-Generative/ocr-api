import os
import pytest
from openai import OpenAI
from business.llm.models.base import VisionLLMOCR
from business.llm.models.template import TemplateLLMDetector
from PIL import Image

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
VISION_MODEL = os.environ.get("VISION_MODEL")
INSTRUCT_MODEL_NAME = os.environ.get("INSTRUCT_MODEL_NAME")


@pytest.mark.skipif(
    condition=not all([OPENAI_API_KEY, OPENAI_BASE_URL, VISION_MODEL, INSTRUCT_MODEL_NAME]),
    reason="Client Openai is not set",
)
def test_vision_extraction():
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    obj = VisionLLMOCR(client=client, model_name=VISION_MODEL)
    obj_template = TemplateLLMDetector(client=client, model_name=INSTRUCT_MODEL_NAME)
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    pages = obj.batch_predict(images=[image])
    assert len(pages) == 1
    assert len(pages[0].boxes) == 1
    assert pages[0].boxes[0].text

    pages = obj_template.batch_predict(images=[image], pages=pages)
    assert len(pages[0].form_entries) > -1
