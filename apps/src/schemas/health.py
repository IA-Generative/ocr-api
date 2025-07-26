from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class Health(BaseModel):
    name: str
    version: str
    up_time: str
    extras: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    dependencies: Optional[List[Union["Health"]]] = None
