import pytest
import sys
from pathlib import Path


path_to_task = Path(__file__).parent.parent.parent.parent.parent / "apps" / "server"


@pytest.fixture(scope="session", autouse=True)
def add_server_src_to_sys_path():
    if not path_to_task.exists():
        raise FileNotFoundError(f"Le chemin {path_to_task} n'existe pas.")
    sys.path.insert(0, str(path_to_task))
    yield
    sys.path.remove(str(path_to_task))


def test_check_same_task_models():
    # Check that the models in src/schemas and sdk/ocr_sdk are the same
    from src.schemas.task import TaskModel
    from ocr_sdk.schemas.task import TaskModel as SDKTaskModel

    assert TaskModel.model_json_schema() == SDKTaskModel.model_json_schema()


def test_check_same_health_models():
    # Check that the models in src/schemas and sdk/ocr_sdk are the same
    from src.schemas.health import Health
    from ocr_sdk.schemas.health import Health as SDKHealthModel

    assert Health.model_json_schema() == SDKHealthModel.model_json_schema()
