import os
import pytest
from openai import OpenAI
from business.llm.models.template import FormFieldExtractor
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.schemas.template import LLMFormField

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
INSTRUCT_MODEL_NAME = os.environ.get("INSTRUCT_MODEL_NAME")


@pytest.mark.skipif(
    condition=not all([OPENAI_API_KEY, OPENAI_BASE_URL, INSTRUCT_MODEL_NAME]),
    reason="Client Openai is not set",
)
def test_llm_template_extractor_integration():
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    obj = FormFieldExtractor(client=client, model_name=INSTRUCT_MODEL_NAME)
    text = """
    Nom: Roger
    Prenom: Jean
    Adresse: 5 route de la lumiere 75001 Paris
    numero: 0123456789
    [x] : propietaire [ ]: Locataire
    """

    pages = obj.batch_predict(
        images=[],
        pages=[
            Page(
                page=1,
                boxes=[Bbox(x=0, y=0, width=1, height=1, confidence=1, text=text)],
            )
        ],
    )

    assert len(pages) == 1
    assert len(pages[0].form_entries) > 0
    assert isinstance(pages[0].form_entries[0], LLMFormField)


@pytest.mark.skipif(
    condition=not all([OPENAI_API_KEY, OPENAI_BASE_URL, INSTRUCT_MODEL_NAME]),
    reason="Client Openai is not set",
)
def test_llm_template_extractor_with_correction_integration():
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    obj = FormFieldExtractor(client=client, model_name=INSTRUCT_MODEL_NAME)
    text = """
    Formulaire d'inscription
    Name Roger
    Pranom: Jean
    Adress: 5 route de la lumiere 75001 Paris
    numer: 0123456789
    [x] : propietire [ ]: Loctaire
    """

    pages = obj.batch_predict(
        images=[],
        pages=[
            Page(
                page=1,
                boxes=[Bbox(x=0, y=0, width=1, height=1, confidence=1, text=text)],
            )
        ],
    )

    assert len(pages) == 1
    assert len(pages[0].form_entries) > 0
    assert isinstance(pages[0].form_entries[0], LLMFormField)


def test_llm_template_extractor_with_correction_unit(monkeypatch: pytest.MonkeyPatch):
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    obj = FormFieldExtractor(client=client, model_name=INSTRUCT_MODEL_NAME)
    monkeypatch.setattr(
        type(obj.instructor.chat.completions),
        "create",
        lambda self, *args, **kwargs: [
            LLMFormField(name="Name", value="Roger", type="checkbox", filled=True, sections=[]),
            LLMFormField(name="Prénom", value="Jean", type="text", filled=True, sections=[]),
            LLMFormField(
                name="Adresse",
                value="5 route de la lumiere 75001 Paris",
                type="text",
                filled=True,
                sections=[],
            ),
            LLMFormField(name="Numéro", value="0123456789", type="text", filled=True, sections=[]),
            LLMFormField(
                name="propietire",
                value="[x]",
                type="checkbox",
                filled=True,
                sections=[],
            ),
            LLMFormField(name="Numéro", value="0123456789", type="text", filled=True, sections=[]),
            LLMFormField(
                name="propietire",
                value="[x]",
                type="checkbox",
                filled=True,
                sections=[],
            ),
            LLMFormField(name="Loctaire", value="[ ]", type="checkbox", filled=False, sections=[]),
        ],
    )
    text = """
    Formulaire d'inscription
    Name Roger
    Pranom: Jean
    Adress: 5 route de la lumiere 75001 Paris
    numer: 0123456789
    [x] : propietire [ ]: Loctaire
    """

    pages = obj.batch_predict(
        images=[],
        pages=[
            Page(
                page=1,
                boxes=[Bbox(x=0, y=0, width=1, height=1, confidence=1, text=text)],
            )
        ],
    )

    assert len(pages) == 1
    assert len(pages[0].form_entries) > 0
    assert isinstance(pages[0].form_entries[0], LLMFormField)
