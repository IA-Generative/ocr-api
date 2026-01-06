import pytest
from openai import OpenAI
import os
from PIL import Image
from business.llm.models.classification import FormClassification
from src.schemas.template import ImageFormDetector
from src.schemas.output import Page

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
VISION_MODEL = os.environ.get("VISION_MODEL")


@pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
def test_vision_extraction_only_unit(monkeypatch: pytest.MonkeyPatch):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )

    obj = FormClassification(client=client, model_name=VISION_MODEL)
    monkeypatch.setattr(
        type(obj.client.chat.completions),
        "create",
        lambda self, *args, **kwargs: ImageFormDetector(is_form=True, confidence=0.95),
    )
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    result: list[Page] = obj.batch_predict(images=[image])
    assert len(result) == 1
    assert isinstance(result[0].image_form_detector, ImageFormDetector)
