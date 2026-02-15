from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Union, Dict, Any


class Vector(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    collection_name: Optional[str] = None
    model_name: str
    vector: list[float]
    vector_size: int
    label: str
    source_id: Optional[str] = None
    page_num: Optional[int] = 0


class VectorSearchResult(BaseModel):
    """Résultat d'une recherche vectorielle générique"""

    id: Union[str, int]
    score: float
    payload: Optional[Dict[str, Any]] = None
    vector: Optional[List[float]] = None
