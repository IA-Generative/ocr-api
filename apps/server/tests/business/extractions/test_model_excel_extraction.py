from business.extractions.models.excel_extraction import ExcelExtractionModel

from src.schemas.task import TaskModel
from src.schemas.input import InputForm


def test_excel_extraction_model_is_applicable():
    model = ExcelExtractionModel()
    task = TaskModel(
        id="1",
        type="DEFAULT",
        user_id="user_1",
        created_at=200000000,
        updated_at=200000000,
        input=InputForm(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            storage_file_path="s3://bucket/file.xlsx",
            raw_filename="file.xlsx",
            ext=".xlsx",
            size=1234,
        ),
    )
    assert model.is_applicable(task) is True

    task.input.content_type = "application/pdf"
    assert model.is_applicable(task) is False


def test_excel_extraction_model_batch_predict():
    model = ExcelExtractionModel()
    with open("tests/data/file_example_XLSX_10.xlsx", "rb") as f:
        test_xlsx_content = f.read()
    images = [test_xlsx_content]

    pages = model.batch_predict(images)

    assert len(pages) == 1
