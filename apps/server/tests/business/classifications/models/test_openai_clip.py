import pytest

from business.classification.models.openai_clip import OpenAIClipModel
from src.schemas.classification import LabelDefinition
from src.schemas.output import Page
from PIL import Image


@pytest.fixture
def labels() -> list[LabelDefinition]:
    return [
        LabelDefinition(label="Facture", definition="Document de facturation"),
        LabelDefinition(label="Relevé de compte", definition="Document bancaire"),
        LabelDefinition(label="Contrat de travail", definition="Document d'emploi"),
        LabelDefinition(label="Pièce d'identité", definition="Document d'identification"),
        LabelDefinition(label="Autre document", definition="Document non classifié"),
    ]


def test_openai_clip_classification(labels: list[LabelDefinition]):
    model = OpenAIClipModel(model_name="ViT-L/14", device="cpu")

    # Charger une image de test

    image_path = "tests/data/valid/identite.jpg"
    image = Image.open(image_path)

    # Effectuer la classification
    pages = [Page(page=0)]
    result_pages = model.batch_predict(images=[image], pages=pages, labels=labels)

    # Vérifier les résultats
    assert len(result_pages) == 1
    classifications = result_pages[0].classifications
    assert len(classifications) == len(labels)
    for classification in classifications:
        assert classification.label in labels
        assert 0.0 <= classification.confidence <= 1.0
