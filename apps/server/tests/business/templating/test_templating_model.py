from business.templating.model import TemplatingFieldExtraction


def test_templating_field_extraction_empty():
    # Create a sample ODT file with placeholders
    tmp_path = "tests/data/valid/file-sample_100kB.odt"

    extractor = TemplatingFieldExtraction()
    valid_fields, invalid_fields = extractor.process(str(tmp_path))

    assert valid_fields == []
    assert invalid_fields == []


def test_templating_field_extraction_valid():
    # Create a sample ODT file with placeholders
    tmp_path = "tests/data/valid/file-sample_100kB-valid.odt"

    extractor = TemplatingFieldExtraction()
    valid_fields, invalid_fields = extractor.process(str(tmp_path))

    assert valid_fields == [
        "valid_placeholder1",
        "valid_placeholder2",
        "valid_placeholder1",
    ]
    assert invalid_fields == []


def test_templating_field_extraction_invalid():
    # Create a sample ODT file with placeholders
    tmp_path = "tests/data/invalid/file-sample_100kB-invalid.odt"

    extractor = TemplatingFieldExtraction()
    valid_fields, invalid_fields = extractor.process(str(tmp_path))

    assert valid_fields == [
        "valid_placeholder1",
        "valid_placeholder2",
    ]
    assert invalid_fields == ["valid_placeholder 1"]
