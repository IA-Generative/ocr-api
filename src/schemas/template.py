from pydantic import BaseModel, Field
from typing import List


class FormEntry(BaseModel):
    key: str = Field(..., description="Nom brut du champ extrait")
    value: str = Field(..., description="Valeur brute extraite")
    corrected_key: str = Field(..., description="Nom de champ corrigé (typo, casse…)")
    corrected_value: str = Field(..., description="Valeur corrigée (format date, nombres…)")


class FormExtraction(BaseModel):
    entries: List[FormEntry] = Field(..., description="Liste des champs extraits et corrigés")
