import os
import pytest
from openai import OpenAI
from business.llm.models.template import TemplateLLMDetector
from src.schemas.output import Page
from src.schemas.box import Bbox
from src.schemas.template import FormExtraction, FormEntry

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL")
INSTRUCT_MODEL_NAME = os.environ.get("INSTRUCT_MODEL_NAME")


@pytest.mark.skipif(
    condition=not all([OPENAI_API_KEY, OPENAI_BASE_URL, INSTRUCT_MODEL_NAME]),
    reason="Client Openai is not set",
)
def test_llm_template_extractor():
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    obj = TemplateLLMDetector(client=client, model_name=INSTRUCT_MODEL_NAME)
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
    _ = FormExtraction(
        entries=[
            FormEntry(key="Nom", value="Roger", corrected_key=None, corrected_value=None),
            FormEntry(key="Prenom", value="Jean", corrected_key=None, corrected_value=None),
            FormEntry(
                key="Adresse",
                value="5 route de la lumiere 75001 Paris",
                corrected_key=None,
                corrected_value=None,
            ),
            FormEntry(
                key="numero",
                value="0123456789",
                corrected_key=None,
                corrected_value=None,
            ),
            FormEntry(key="propietaire", value="[x]", corrected_key=None, corrected_value=None),
            FormEntry(key="Locataire", value="[ ]", corrected_key=None, corrected_value=None),
        ]
    )
    assert len(pages) == 1
    assert len(pages[0].form_entries) > 0
    assert isinstance(pages[0].form_entries[0], FormEntry)


@pytest.mark.skipif(
    condition=not all([OPENAI_API_KEY, OPENAI_BASE_URL, INSTRUCT_MODEL_NAME]),
    reason="Client Openai is not set",
)
def test_llm_template_extractor_with_correction():
    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )
    obj = TemplateLLMDetector(client=client, model_name=INSTRUCT_MODEL_NAME)
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
    _ = FormExtraction(
        entries=[
            FormEntry(key="Name", value="Roger", corrected_key=None, corrected_value=None),
            FormEntry(key="Pranom", value="Jean", corrected_key=None, corrected_value=None),
            FormEntry(
                key="Adress",
                value="5 route de la lumiere 75001 Paris",
                corrected_key=None,
                corrected_value=None,
            ),
            FormEntry(
                key="numer",
                value="0123456789",
                corrected_key=None,
                corrected_value=None,
            ),
            FormEntry(key="propietire", value="[x]", corrected_key=None, corrected_value=None),
            FormEntry(key="Loctaire", value="[ ]", corrected_key=None, corrected_value=None),
        ]
    )
    assert len(pages) == 1
    assert len(pages[0].form_entries) > 0
    assert isinstance(pages[0].form_entries[0], FormEntry)
