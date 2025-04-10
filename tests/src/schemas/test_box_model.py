import pytest
from pydantic import ValidationError
from src.schemas.box import Box


def test_box_valid():
    data = {
        "text": "Bonjour",
        "text_region": [[0, 0], [10, 0], [10, 10], [0, 10]],
        "confidence": 0.95,
    }
    box = Box(**data)
    assert box.text == "Bonjour"
    assert box.confidence == 0.95
    assert box.text_region == [[0, 0], [10, 0], [10, 10], [0, 10]]


def test_box_invalid_confidence():
    data = {
        "text": "Test",
        "text_region": [[0, 0], [1, 1]],
        "confidence": "not-a-float",
    }
    with pytest.raises(ValidationError):
        Box(**data)


def test_box_invalid_text_region():
    data = {"text": "Test", "text_region": "invalid", "confidence": 0.9}
    with pytest.raises(ValidationError):
        Box(**data)
