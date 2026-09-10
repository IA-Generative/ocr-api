"""Sync client for OCR API."""

import time
from pathlib import Path
from typing import List, Optional, Union

import httpx

from ocr_sdk.models import Health, TaskModel, TaskOperation, TaskStatus
from ocr_sdk.exceptions import OCRAPIError, OCRTimeoutError


class SyncOCRClient:
    """Synchronous client for OCR API.

    Example:
        >>> with SyncOCRClient("http://localhost:5000") as client:
        ...     # Upload a file for OCR processing
        ...     task = client.create_job("path/to/file.pdf")
        ...     # Wait for completion
        ...     result = client.wait_for_task(task.id)
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize the sync OCR client.

        Args:
            base_url: Base URL of the OCR API (e.g., "http://localhost:5000")
            api_key: Optional API key for authentication
            timeout: Default timeout for requests in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    def __enter__(self):
        """Context manager entry."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._client:
            self._client.close()

    def _ensure_client(self):
        """Ensure client is initialized."""
        if self._client is None:
            raise RuntimeError(
                "Client not initialized. Use 'with SyncOCRClient(...) as client:'"
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        """Make an HTTP request."""
        self._ensure_client()

        try:
            response = self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response
        except httpx.TimeoutException as e:
            raise OCRTimeoutError(f"Request timed out: {e}")
        except httpx.HTTPStatusError as e:
            raise OCRAPIError(
                status_code=e.response.status_code,
                message=e.response.text,
            )

    def get_health(self) -> Health:
        """Get health status of the API.

        Returns:
            Health object with API status
        """
        response = self._request("GET", "/api/health")
        return Health(**response.json())

    def create_job(
        self,
        file_path: Union[str, Path],
        group_id: str = "DEFAULT",
        interest_zone: Optional[str] = None,
        task_operation: TaskOperation = TaskOperation.DEFAULT,
    ) -> TaskModel:
        """Create a new OCR job.

        Args:
            file_path: Path to the file to process
            group_id: Group ID for the task
            interest_zone: Optional JSON string defining regions of interest
            task_operation: Type of operation to perform

        Returns:
            TaskModel with job details
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Prepare form data
        with open(file_path, "rb") as f:
            files = {
                "file": (file_path.name, f),
            }

            data = {
                "group_id": group_id,
                "task_operation": task_operation.value,
            }

            if interest_zone:
                data["interest_zone"] = interest_zone

            response = self._request(
                "POST",
                "/api/jobs/",
                files=files,
                data=data,
            )

        return TaskModel(**response.json())

    def get_task(self, task_id: str) -> TaskModel:
        """Get task details by ID.

        Args:
            task_id: Task ID

        Returns:
            TaskModel with task details
        """
        response = self._request("GET", f"/api/tasks/{task_id}")
        return TaskModel(**response.json())

    def get_user_tasks(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> List[TaskModel]:
        """Get tasks for the authenticated user.

        Args:
            page: Page number (1-indexed)
            page_size: Number of tasks per page

        Returns:
            List of TaskModel objects
        """
        response = self._request(
            "GET",
            "/api/tasks/user/",
            params={"page": page, "page_size": page_size},
        )
        return [TaskModel(**task) for task in response.json()]

    def wait_for_task(
        self,
        task_id: str,
        poll_interval: float = 2.0,
        max_wait_time: float = 300.0,
    ) -> TaskModel:
        """Wait for a task to complete.

        Args:
            task_id: Task ID
            poll_interval: Time between status checks in seconds
            max_wait_time: Maximum time to wait in seconds

        Returns:
            Completed TaskModel

        Raises:
            OCRTimeoutError: If task doesn't complete within max_wait_time
            OCRAPIError: If task fails
        """
        elapsed = 0.0

        while elapsed < max_wait_time:
            task = self.get_task(task_id)

            if task.status == TaskStatus.COMPLETED.value:
                return task
            elif task.status == TaskStatus.FAILED.value:
                error = (
                    task.extras.get("error", "Unknown error")
                    if task.extras
                    else "Unknown error"
                )
                raise OCRAPIError(500, f"Task failed: {error}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise OCRTimeoutError(
            f"Task {task_id} did not complete within {max_wait_time}s"
        )
