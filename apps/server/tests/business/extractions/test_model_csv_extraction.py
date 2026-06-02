from business.extractions.models.csv_extraction import CSVExtractionModel

from src.schemas.task import TaskModel
from src.schemas.input import InputForm
from services.utils.lazy_file import LazyFileImageList


def test_csv_extraction_model_is_applicable():
    model = CSVExtractionModel()
    task = TaskModel(
        id="1",
        type="DEFAULT",
        user_id="user_1",
        created_at=200000000,
        updated_at=200000000,
        input=InputForm(
            content_type="text/csv",
            storage_file_path="s3://bucket/file.csv",
            raw_filename="file.csv",
            ext=".csv",
            size=1234,
        ),
    )
    assert model.is_applicable(task) is True

    task.input.content_type = "application/pdf"
    assert model.is_applicable(task) is False


def test_csv_extraction_model_batch_predict():

    with open("test.csv", "w") as f:
        f.write("col1,col2,col3\n")
        f.write("1,2,3\n")
        f.write("4,5,6\n")

    images = LazyFileImageList("test.csv")
    model = CSVExtractionModel(parser_result=images.info)

    pages = model.batch_predict(images)

    assert len(pages) == 1
