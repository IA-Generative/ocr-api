import os
import pytest
from openai import OpenAI, AsyncOpenAI
from business.llm.models.vision import LLMToForm
from src.schemas.output import LLMFormField, Page
from PIL import Image

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
VISION_MODEL = os.environ.get("VISION_MODEL")


@pytest.mark.skipif(
    condition=not all([OPENAI_API_KEY, OPENAI_BASE_URL, VISION_MODEL]),
    reason="Client Openai is not set",
)
def test_vision_extraction_only():
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    obj = LLMToForm(client=client, model_name=VISION_MODEL)
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    result: list[Page] = obj.batch_predict(images=[image])
    assert len(result) == 1
    assert len(result[0].boxes) == 1
    assert result[0].boxes[0].text
    assert result[0].form_entries != 0
    assert isinstance(result[0].form_entries[0], LLMFormField)

    client = AsyncOpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    obj = LLMToForm(client=client, model_name=VISION_MODEL)
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    result: list[Page] = obj.batch_predict(images=[image], pages=[Page(page=0)])
    assert len(result) == 1
    assert result[0].boxes[0].text
    assert len(result[0].form_entries) != 0
    assert isinstance(result[0].form_entries[0], LLMFormField)


def test_vision_extraction_only_unit(monkeypatch: pytest.MonkeyPatch):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    # Patch la méthode create sur la classe appropriée

    obj = LLMToForm(client=client, model_name=VISION_MODEL)
    monkeypatch.setattr(
        type(obj.client.chat.completions),
        "create",
        lambda self, *args, **kwargs: [LLMFormField(name="field_name", value="field_value", type="text")],
    )
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    result: list[Page] = obj.batch_predict(images=[image])
    assert len(result) == 1
    assert len(result[0].form_entries) != 0
    assert isinstance(result[0].form_entries[0], LLMFormField)
