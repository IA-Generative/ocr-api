from business.extractions.models.libre_extraction import (
    ODTExtractionModel,
    OdpExtractionModel,
    OdsExtractionModel,
)

from src.schemas.task import TaskModel
from src.schemas.input import InputForm


def test_odt_extraction_model_is_applicable():
    model = ODTExtractionModel()
    task = TaskModel(
        id="1",
        type="DEFAULT",
        user_id="user_1",
        created_at=200000000,
        updated_at=200000000,
        input=InputForm(
            content_type="application/vnd.oasis.opendocument.text",
            storage_file_path="s3://bucket/file.odt",
            raw_filename="file.odt",
            ext=".odt",
            size=1234,
        ),
    )
    assert model.is_applicable(task) is True

    task.input.content_type = "application/pdf"
    assert model.is_applicable(task) is False


def test_odt_extraction_model_batch_predict():
    model = ODTExtractionModel()
    with open("tests/data/file-sample_100kB.odt", "rb") as f:
        test_odt_content = f.read()
    images = [test_odt_content]

    pages = model.batch_predict(images)

    assert len(pages) == 1


def test_odp_extraction_model_batch_predict():
    model = OdpExtractionModel()
    with open("tests/data/file_example_ODP_200kB.odp", "rb") as f:
        test_odt_content = f.read()
    images = [test_odt_content]

    pages = model.batch_predict(images)

    assert len(pages) == 1
    assert pages[0].boxes


def test_ods_extraction_model_batch_predict():
    model = OdsExtractionModel()
    with open("tests/data/file_example_ODS_10.ods", "rb") as f:
        test_odt_content = f.read()
    images = [test_odt_content]

    pages = model.batch_predict(images)

    assert len(pages) == 1
    assert pages[0].boxes
