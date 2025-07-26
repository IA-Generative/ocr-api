from pydantic import BaseModel, Field
from typing import List, Optional


class FormEntry(BaseModel):
    key: str = Field(..., description="Nom brut du champ extrait")
    value: str = Field(..., description="Valeur brute extraite")
    corrected_key: Optional[str] = Field(
        None,
        description="Nom de champ corrigé (typo, casse, orthographe …) de key si besoin",
    )
    corrected_value: Optional[str] = Field(
        None,
        description="Valeur corrigée (typo, casse, format date, nombres, orthographe…) de value si besoin",
    )


class FormExtraction(BaseModel):
    entries: List[FormEntry] = Field(..., description="Liste des champs extraits et corrigés")
