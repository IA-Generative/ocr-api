from typing import Dict, Any, List
from pydantic import BaseModel


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    version: str
    up_time: str
    extras: Dict[str, Any]
    dependencies: List[Any]
