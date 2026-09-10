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
    entries: List[FormEntry] = Field(
        ..., description="Liste des champs extraits et corrigés"
    )


class LLMFormField(BaseModel):
    name: Optional[str] = Field(
        default=None, description="Nom du champ (ex: 'nom', 'adresse')."
    )
    value: Optional[str] = Field(default=None, description="Valeur actuelle du champ.")
    type: str = Field(..., description="Type de champ.")
    sections: Optional[List[str]] = Field(
        default=None, description="Sections auxquelles appartient le champ."
    )
    filled: Optional[bool] = Field(
        default=None, description="Indique si le champ est rempli."
    )


class ImageFormDetector(BaseModel):
    is_form: bool = Field(
        ..., description="Indique si l'image est un formulaire ou non."
    )
    confidence: float = Field(..., description="Confiance de la classification (0-1).")
