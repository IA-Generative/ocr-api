import pytest
from services.utils.validation import validate_task


def test_validate_task():
    with pytest.raises(ValueError):
        validate_task("invalid json")
