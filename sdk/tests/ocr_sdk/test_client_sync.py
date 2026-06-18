import pytest
from ocr_sdk.client_sync import SyncOCRClient
from ocr_sdk.client_async import AsyncOCRClient
from pathlib import Path


@pytest.fixture(scope="module")
def path_to_test_file() -> str:
    """Helper function to get the absolute path to a test file."""
    path = Path(__file__).parent.parent.parent.parent / \
        "apps"/"server"/"tests"/"data"/"valid"/"identite.jpg"

    if not path.is_file():
        pytest.skip(f"Test file not found: {path}")
    return str(path)


def test_sync_client(path_to_test_file: str, api_ready):
    with SyncOCRClient(base_url="http://localhost:5000", api_key="default-api-key") as client:
        health = client.get_health()
        assert health.status == "healthy"
        task = client.create_job(
            file_path=path_to_test_file,
        )
        assert task.status == "queued"

        result = client.wait_for_task(
            task.id, max_wait_time=300, poll_interval=5)
        assert result.status == "completed"


@pytest.mark.asyncio
async def test_async_client(path_to_test_file: str, api_ready):
    async with AsyncOCRClient(base_url="http://localhost:5000", api_key="default-api-key") as client:
        health = await client.get_health()
        assert health.status == "healthy"
        task = await client.create_job(
            file_path=path_to_test_file,
        )
        assert task.status == "queued"

        result = await client.wait_for_task(
            task.id, max_wait_time=300, poll_interval=5)
        assert result.status == "completed"
