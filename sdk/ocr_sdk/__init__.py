"""OCR SDK - Python client for OCR API."""

from ocr_sdk.client_async import AsyncOCRClient
from ocr_sdk.client_sync import SyncOCRClient
from ocr_sdk.models import (
    TaskModel,
    TaskStatus,
    TaskOperation,
    Health,
    OCRResult,
    Page,
    Bbox,
)

__version__ = "0.1.2"

__all__ = [
    "AsyncOCRClient",
    "SyncOCRClient",
    "TaskModel",
    "TaskStatus",
    "TaskOperation",
    "Health",
    "OCRResult",
    "Page",
    "Bbox",
]
