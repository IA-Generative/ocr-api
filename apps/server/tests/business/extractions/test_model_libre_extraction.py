from business.extractions.models.libre_extraction import (
    ODTExtractionModel,
    OdpExtractionModel,
    OdsExtractionModel,
)

from src.schemas.task import TaskModel
from src.schemas.input import InputForm
from services.utils.lazy_file import LazyFileImageList


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

    task.input.content_type = "application/pdf"  # noqa
    assert model.is_applicable(task) is False


def test_odt_extraction_model_batch_predict():
    images = LazyFileImageList("tests/data/file-sample_100kB.odt")
    model = ODTExtractionModel(parser_result=images.info)

    pages = model.batch_predict(images)

    assert len(pages) == 4
    assert pages[0].boxes


def test_odp_extraction_model_batch_predict():
    images = LazyFileImageList("tests/data/file_example_ODP_200kB.odp")
    model = OdpExtractionModel(parser_result=images.info)

    pages = model.batch_predict(images)

    assert len(pages) == 3
    assert pages[0].boxes


def test_ods_extraction_model_batch_predict():
    images = LazyFileImageList("tests/data/file_example_ODS_10.ods")
    model = OdsExtractionModel(parser_result=images.info)

    pages = model.batch_predict(images)

    assert len(pages) == 2
    assert pages[0].boxes
