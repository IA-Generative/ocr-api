"""Async client for OCR API."""

import asyncio
from pathlib import Path
from typing import List, Optional, Union

import httpx

from ocr_sdk.models import (
    Health,
    TaskModel,
    TaskOperation,
    TaskStatus,
    ProcessResponse,
)
from ocr_sdk.exceptions import OCRAPIError, OCRTimeoutError


class AsyncOCRClient:
    """Async client for OCR API.
    
    Example:
        >>> async with AsyncOCRClient("http://localhost:5000") as client:
        ...     # Upload a file for OCR processing
        ...     task = await client.create_job("path/to/file.pdf")
        ...     # Wait for completion
        ...     result = await client.wait_for_task(task.id)
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """Initialize the async OCR client.
        
        Args:
            base_url: Base URL of the OCR API (e.g., "http://localhost:5000")
            api_key: Optional API key for authentication
            timeout: Default timeout for requests in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    def _ensure_client(self):
        """Ensure client is initialized."""
        if self._client is None:
            raise RuntimeError(
                "Client not initialized. Use 'async with AsyncOCRClient(...) as client:'"
            )

    async def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        """Make an HTTP request."""
        self._ensure_client()
        
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response
        except httpx.TimeoutException as e:
            raise OCRTimeoutError(f"Request timed out: {e}")
        except httpx.HTTPStatusError as e:
            raise OCRAPIError(
                status_code=e.response.status_code,
                message=e.response.text,
            )

    async def get_health(self) -> Health:
        """Get health status of the API.
        
        Returns:
            Health object with API status
        """
        response = await self._request("GET", "/api/health")
        return Health(**response.json())

    async def create_job(
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
        files = {
            "file": (file_path.name, open(file_path, "rb")),
        }
        
        data = {
            "group_id": group_id,
            "task_operation": task_operation.value,
        }
        
        if interest_zone:
            data["interest_zone"] = interest_zone
        
        response = await self._request(
            "POST",
            "/api/jobs/",
            files=files,
            data=data,
        )
        
        return TaskModel(**response.json())

    async def get_task(self, task_id: str) -> TaskModel:
        """Get task details by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            TaskModel with task details
        """
        response = await self._request("GET", f"/api/tasks/{task_id}")
        return TaskModel(**response.json())

    async def get_user_tasks(
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
        response = await self._request(
            "GET",
            "/api/tasks/user/",
            params={"page": page, "page_size": page_size},
        )
        return [TaskModel(**task) for task in response.json()]

    async def get_task_text(self, task_id: str) -> str:
        """Get extracted text from a completed task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Extracted text content
        """
        response = await self._request("GET", f"/api/text-task/{task_id}")
        return response.text

    async def wait_for_task(
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
            task = await self.get_task(task_id)
            
            if task.status == TaskStatus.COMPLETED.value:
                return task
            elif task.status == TaskStatus.FAILED.value:
                error = task.extras.get("error", "Unknown error") if task.extras else "Unknown error"
                raise OCRAPIError(500, f"Task failed: {error}")
            
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
        
        raise OCRTimeoutError(f"Task {task_id} did not complete within {max_wait_time}s")

    async def process_document(
        self,
        file_path: Union[str, Path],
        max_wait_time: int = 300,
        poll_interval: int = 2,
    ) -> List[ProcessResponse]:
        """Process a document and wait for results.
        
        This is a convenience method that uploads a file and waits for processing.
        
        Args:
            file_path: Path to the file to process
            max_wait_time: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
            
        Returns:
            List of ProcessResponse objects with page content and metadata
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file content
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Set headers
        headers = {
            "X-Filename": file_path.name,
            "Content-Type": "application/octet-stream",
            "Max-Wait-Time": str(max_wait_time),
            "Poll-Interval": str(poll_interval),
        }
        
        response = await self._request(
            "PUT",
            "/api/process",
            content=file_content,
            headers=headers,
        )
        
        return [ProcessResponse(**item) for item in response.json()]
