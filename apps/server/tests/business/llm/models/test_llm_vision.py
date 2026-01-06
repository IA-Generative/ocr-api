import os
import pytest
from openai import OpenAI
from business.llm.models.base import VisionLLMOCR
from PIL import Image

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
VISION_MODEL = os.environ.get("VISION_MODEL")


@pytest.mark.skipif(
    condition=not all([OPENAI_API_KEY, OPENAI_BASE_URL, VISION_MODEL]),
    reason="Client Openai is not set",
)
def test_vision_extraction_integration():
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    obj = VisionLLMOCR(client=client, model_name=VISION_MODEL)
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    result = obj.batch_predict(images=[image])
    assert len(result) == 1
    assert len(result[0].boxes) == 1
    assert result[0].boxes[0].text


@pytest.mark.skipif(not OPENAI_API_KEY, reason="OPENAI_API_KEY not set")
def test_vision_extraction(monkeypatch: pytest.MonkeyPatch):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    # Patch la méthode create sur la classe appropriée
    monkeypatch.setattr(
        type(client.chat.completions),
        "create",
        lambda self, *args, **kwargs: type(
            "Resp",
            (),
            {
                "choices": [
                    type(
                        "Choice",
                        (),
                        {
                            "message": type("Msg", (), {"content": "Mock response"})(),
                            "finish_reason": "stop",  # Ajouté ici
                        },
                    )()
                ]
            },
        )(),
    )
    obj = VisionLLMOCR(client=client, model_name=VISION_MODEL)
    image_path = "tests/data/valid/formulaire-cerfa-complete.png"
    image = Image.open(image_path).convert("RGB")
    result = obj.batch_predict(images=[image])
    assert len(result) == 1
    assert len(result[0].boxes) == 1
    assert result[0].boxes[0].text
