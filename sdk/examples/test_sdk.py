"""Simple test to validate SDK structure and imports."""

import sys
from pathlib import Path

# Add SDK to path for testing
sdk_path = Path(__file__).parent.parent
sys.path.insert(0, str(sdk_path))


def test_imports():
    """Test that all public API can be imported."""
    from ocr_sdk import (
        AsyncOCRClient,
        SyncOCRClient,
        TaskModel,
        TaskStatus,
        TaskOperation,
        Health,
        OCRResult,
        Page,
        Bbox,
    )
    
    assert AsyncOCRClient is not None
    assert SyncOCRClient is not None
    assert TaskModel is not None
    assert TaskStatus is not None
    assert TaskOperation is not None
    assert Health is not None
    assert OCRResult is not None
    assert Page is not None
    assert Bbox is not None
    
    print("✓ All imports successful")


def test_task_status_enum():
    """Test TaskStatus enum values."""
    from ocr_sdk import TaskStatus
    
    assert TaskStatus.CREATED.value == "created"
    assert TaskStatus.QUEUED.value == "queued"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.FAILED.value == "failed"
    
    print("✓ TaskStatus enum validated")


def test_task_operation_enum():
    """Test TaskOperation enum values."""
    from ocr_sdk import TaskOperation
    
    assert TaskOperation.DEFAULT.value == "default"
    assert TaskOperation.OCR.value == "ocr"
    assert TaskOperation.FORMS.value == "forms"
    
    print("✓ TaskOperation enum validated")


def test_sync_client_initialization():
    """Test SyncOCRClient initialization."""
    from ocr_sdk import SyncOCRClient
    
    client = SyncOCRClient("http://localhost:5000")
    assert client.base_url == "http://localhost:5000"
    assert client.timeout == 30.0
    
    client_with_auth = SyncOCRClient(
        "http://localhost:5000",
        api_key="test-token",
        timeout=60.0
    )
    assert client_with_auth.api_key == "test-token"
    assert client_with_auth.timeout == 60.0
    
    print("✓ SyncOCRClient initialization validated")


def test_async_client_initialization():
    """Test AsyncOCRClient initialization."""
    from ocr_sdk import AsyncOCRClient
    
    client = AsyncOCRClient("http://localhost:5000")
    assert client.base_url == "http://localhost:5000"
    assert client.timeout == 30.0
    
    client_with_auth = AsyncOCRClient(
        "http://localhost:5000",
        api_key="test-token",
        timeout=60.0
    )
    assert client_with_auth.api_key == "test-token"
    assert client_with_auth.timeout == 60.0
    
    print("✓ AsyncOCRClient initialization validated")


def test_pydantic_models():
    """Test Pydantic model creation."""
    from ocr_sdk.models import TaskModel, Bbox, Page
    
    # Test Bbox
    bbox = Bbox(x=0.1, y=0.2, width=0.3, height=0.4, text="test")
    assert bbox.x == 0.1
    assert bbox.text == "test"
    
    # Test Page
    page = Page(page=1, boxes=[bbox])
    assert page.page == 1
    assert len(page.boxes) == 1
    
    print("✓ Pydantic models validated")


def test_exceptions():
    """Test custom exceptions."""
    from ocr_sdk.exceptions import (
        OCRSDKError,
        OCRAPIError,
        OCRTimeoutError,
        OCRAuthenticationError,
    )
    
    # Test base exception
    try:
        raise OCRSDKError("test error")
    except OCRSDKError as e:
        assert str(e) == "test error"
    
    # Test API error
    try:
        raise OCRAPIError(404, "Not found")
    except OCRAPIError as e:
        assert e.status_code == 404
        assert e.message == "Not found"
    
    # Test timeout error
    try:
        raise OCRTimeoutError("Timeout")
    except OCRTimeoutError as e:
        assert str(e) == "Timeout"
    
    print("✓ Custom exceptions validated")


if __name__ == "__main__":
    print("Running SDK validation tests...\n")
    
    test_imports()
    test_task_status_enum()
    test_task_operation_enum()
    test_sync_client_initialization()
    test_async_client_initialization()
    test_pydantic_models()
    test_exceptions()
    
    print("\n✅ All validation tests passed!")
    print("SDK is properly configured and ready to use.")
