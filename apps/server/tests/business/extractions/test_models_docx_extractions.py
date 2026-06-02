from business.extractions.models.docx_extraction import DocxExtractionModel

from src.schemas.task import TaskModel
from src.schemas.input import InputForm
from services.utils.lazy_file import LazyFileImageList


def test_docs_extraction_model_is_applicable():
    model = DocxExtractionModel()
    task = TaskModel(
        id="1",
        type="DEFAULT",
        user_id="user_1",
        created_at=200000000,
        updated_at=200000000,
        input=InputForm(
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            storage_file_path="s3://bucket/file.docx",
            raw_filename="file.docx",
            ext=".docx",
            size=1234,
        ),
    )
    assert model.is_applicable(task) is True

    task.input.content_type = "application/pdf"
    assert model.is_applicable(task) is False


def test_docx_extraction_model_batch_predict():
    images = LazyFileImageList("tests/data/valid/file-sample_500kB.docx")
    model = DocxExtractionModel(parser_result=images.info)

    pages = model.batch_predict(images)

    assert len(pages) == 5
    assert pages[0].boxes
