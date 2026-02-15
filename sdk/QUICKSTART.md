# Quick Start Guide

## Installation

### Using uv (Recommended)

#### From Git Repository

```bash
# Install directly from the repository
uv add git@github.com:IA-Generative/ocr-api.git#subdirectory=sdk
```
ou 
```bash
uv add git+ssh://git@github.com/IA-Generative/ocr-api.git#subdirectory=sdk
```

#### From Local Directory

```bash
# Navigate to the SDK directory
cd sdk

# Install the SDK in your project
uv pip install -e .
```

### Using pip

```bash
cd sdk
pip install -e .
```

## Basic Usage

### Sync Client (Simple)

```python
from ocr_sdk import SyncOCRClient

# Create client
with SyncOCRClient("http://localhost:5000") as client:
    # Check health
    health = client.get_health()
    print(f"API is {health.status}")
    
    # Process a document
    task = client.create_job("document.pdf")
    result = client.wait_for_task(task.id)
    
    # Get text
    text = client.get_task_text(task.id)
    print(text)
```

### Async Client (Advanced)

```python
import asyncio
from ocr_sdk import AsyncOCRClient

async def process_document():
    async with AsyncOCRClient("http://localhost:5000") as client:
        # Create and wait for job
        task = await client.create_job("document.pdf")
        result = await client.wait_for_task(task.id)
        
        # Get text
        text = await client.get_task_text(task.id)
        print(text)

asyncio.run(process_document())
```

## Import in Your Project

Once installed, you can import the SDK in any Python file:

```python
# Basic imports
from ocr_sdk import SyncOCRClient, AsyncOCRClient

# Models
from ocr_sdk import TaskModel, TaskStatus, TaskOperation, Health

# Exceptions
from ocr_sdk.exceptions import OCRAPIError, OCRTimeoutError
```

## Examples

Check the `examples/` directory for complete usage examples:
- `sync_example.py` - Comprehensive synchronous client example
- `async_example.py` - Comprehensive asynchronous client example with concurrent processing

## API Reference

### SyncOCRClient / AsyncOCRClient

Both clients have the same methods (async methods use `await`):

- `get_health()` - Get API health status
- `create_job(file_path, ...)` - Upload file and create OCR job
- `get_task(task_id)` - Get task details
- `get_user_tasks(page, page_size)` - List user's tasks
- `get_task_text(task_id)` - Get extracted text
- `wait_for_task(task_id, ...)` - Wait for task completion
- `process_document(file_path, ...)` - One-step upload and wait

### Configuration

```python
client = SyncOCRClient(
    base_url="http://localhost:5000",  # API URL
    api_key="your-token",               # Optional auth token
    timeout=30.0                        # Request timeout in seconds
)
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check the [examples/](examples/) directory for complete code examples
- Review the [models.py](ocr_sdk/models.py) to understand all available data structures
