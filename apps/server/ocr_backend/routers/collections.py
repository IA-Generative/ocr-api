import os
from typing import List, Optional
import json
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field, field_validator

from src.connector.collection_manager import init_qdrant_vector_store
from qdrant_client import QdrantClient
from src.connector.vector_store_interface import DistanceMetric
from src.logger import logger
from src.schemas.templates import template_table
from ocr_backend.core.security.token import RequestContext
from ocr_backend.core.security.factory import TokenVerifier

with open("configs/available_feature_extractors.json", "r") as f:
    available_model_feature = json.load(f)

# ===== SCHEMAS =====

MODEL_NAME = os.environ.get("MODEL_FEATURE_NAME", "dummy")
assert MODEL_NAME in available_model_feature, f"Model feature '{MODEL_NAME}' is not available"


class CollectionCreateRequest(BaseModel):
    """Schéma pour la création d'une collection"""

    name: str = Field(..., min_length=1, max_length=100, description="Nom de la collection")
    vector_size: Optional[int] = Field(
        default=None,
        gt=0,
        description="Taille des vecteurs (auto-détectée si non spécifiée)",
    )
    distance: DistanceMetric = Field(default=DistanceMetric.COSINE, description="Métrique de distance")
    on_disk_payload: bool = Field(default=True, description="Stockage des payloads sur disque")
    replication_factor: int = Field(default=1, ge=1, description="Facteur de réplication")
    write_consistency_factor: int = Field(default=1, ge=1, description="Facteur de cohérence d'écriture")

    @field_validator("vector_size")
    @classmethod
    def validate_vector_size(cls, v):
        """Auto-remplit la vector_size avec celle du modèle configuré si non spécifiée"""
        if v is None:
            # Utiliser la taille du modèle configuré
            model_vector_size = available_model_feature[MODEL_NAME]["model_size"]
            logger.info(f"Auto-détection vector_size: {model_vector_size} pour le modèle {MODEL_NAME}")
            return model_vector_size

        # Vérifier que la taille fournie correspond au modèle configuré
        expected_size = available_model_feature[MODEL_NAME]["model_size"]
        if v != expected_size:
            logger.warning(
                f"vector_size fournie ({v}) différente de celle du modèle {MODEL_NAME} ({expected_size}). "
                f"Utilisation de la taille du modèle: {expected_size}"
            )
            return expected_size

        return v

    def model_post_init(self, __context) -> None:
        """Post-traitement après initialisation du modèle"""
        if self.vector_size is None:
            self.vector_size = available_model_feature[MODEL_NAME]["vector_size"]


class CollectionResponse(BaseModel):
    """Schéma de réponse pour une collection"""

    name: str
    vector_size: int
    distance_metric: str
    points_count: int
    status: str


class CollectionStatsResponse(BaseModel):
    """Schéma de réponse pour les statistiques d'une collection"""

    name: str
    points_count: int
    vector_size: Optional[int] = None
    distance_metric: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None


class MessageResponse(BaseModel):
    """Schéma de réponse pour les messages"""

    message: str
    success: bool


# ===== ROUTER =====

router = APIRouter(
    prefix="/collections",
    tags=["collections"],
    responses={404: {"description": "Collection not found"}},
)
vector_store = init_qdrant_vector_store(qdrant_client=QdrantClient(":memory:"))


def verify_admin_access(
    context: RequestContext = Depends(TokenVerifier),
) -> RequestContext:
    """Vérifie que l'utilisateur est un administrateur"""
    if not context.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action. Admin access required.",
        )
    return context


@router.post("/", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection_data: CollectionCreateRequest,
    context: RequestContext = Depends(verify_admin_access),
):
    """
    Créer une nouvelle collection vectorielle (Admin uniquement)

    Args:
        collection_data: Données de la collection à créer
        context: Contexte de la requête (vérifie les droits admin)

    Returns:
        Message de confirmation

    Raises:
        HTTPException: Si l'utilisateur n'est pas admin, si la collection existe déjà ou si la création échoue
    """
    try:
        # Vérifier si la collection existe déjà
        if vector_store.collection_exists(collection_data.name):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Collection '{collection_data.name}' already exists",
            )

        # Créer la collection
        success = vector_store.create_collection(
            collection_name=collection_data.name,
            vector_size=collection_data.vector_size,
            distance=collection_data.distance,
            on_disk_payload=collection_data.on_disk_payload,
            replication_factor=collection_data.replication_factor,
            write_consistency_factor=collection_data.write_consistency_factor,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create collection '{collection_data.name}'",
            )

        logger.info(f"Collection '{collection_data.name}' created successfully by admin user {context.user_id}")
        return MessageResponse(
            message=f"Collection '{collection_data.name}' created successfully",
            success=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating collection '{collection_data.name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/", response_model=List[str])
async def list_collections(context: RequestContext = Depends(TokenVerifier)):
    """
    Lister les collections accessibles à l'utilisateur

    - Admin : Accès à toutes les collections
    - Utilisateur normal : Accès uniquement aux collections correspondant à ses groupes

    Args:
        context: Contexte de la requête (utilisateur connecté)

    Returns:
        Liste des noms de collections accessibles à l'utilisateur

    Raises:
        HTTPException: Si la récupération échoue
    """
    try:
        all_collections = vector_store.list_collections()

        # Si l'utilisateur est admin, retourner toutes les collections
        if context.is_admin:
            logger.info(f"Retrieved {len(all_collections)} collections for admin user {context.user_id}")
            return all_collections

        # Pour les utilisateurs normaux, filtrer selon leurs groupes
        user_groups = getattr(context, "groups", [])  # Récupérer les groupes de l'utilisateur

        # Filtrer les collections qui correspondent aux groupes de l'utilisateur
        accessible_collections = [collection for collection in all_collections if collection in user_groups]

        logger.info(
            f"Retrieved {len(accessible_collections)} accessible collections for user {context.user_id} "
            f"(groups: {user_groups})"
        )
        return accessible_collections

    except Exception as e:
        logger.error(f"Error listing collections for user {context.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list collections: {str(e)}",
        )


@router.get("/{collection_name}", response_model=CollectionResponse)
async def get_collection(collection_name: str, context: RequestContext = Depends(verify_admin_access)):
    """
    Récupérer les informations d'une collection (Admin uniquement)

    Args:
        collection_name: Nom de la collection
        context: Contexte de la requête (vérifie les droits admin)

    Returns:
        Informations de la collection

    Raises:
        HTTPException: Si l'utilisateur n'est pas admin, si la collection n'existe pas ou si la récupération échoue
    """
    try:
        # Vérifier si la collection existe
        if not vector_store.collection_exists(collection_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection_name}' not found",
            )

        # Récupérer les informations
        collection_info = vector_store.get_collection_info(collection_name)

        if not collection_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve collection '{collection_name}' information",
            )

        return CollectionResponse(
            name=collection_info.name,
            vector_size=collection_info.vector_size,
            distance_metric=collection_info.distance_metric,
            points_count=collection_info.points_count,
            status=collection_info.status,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection '{collection_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.get("/{collection_name}/stats", response_model=CollectionStatsResponse)
async def get_collection_stats(collection_name: str, context: RequestContext = Depends(verify_admin_access)):
    """
    Récupérer les statistiques d'une collection (Admin uniquement)

    Args:
        collection_name: Nom de la collection
        context: Contexte de la requête (vérifie les droits admin)

    Returns:
        Statistiques de la collection

    Raises:
        HTTPException: Si l'utilisateur n'est pas admin, si la collection n'existe pas ou si la récupération échoue
    """
    try:
        # Vérifier si la collection existe
        if not vector_store.collection_exists(collection_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection_name}' not found",
            )

        # Récupérer les statistiques
        stats = vector_store.get_collection_stats(collection_name)

        return CollectionStatsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection stats '{collection_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.delete("/{collection_name}", response_model=MessageResponse)
async def delete_collection(collection_name: str, context: RequestContext = Depends(verify_admin_access)):
    """
    Supprimer une collection et tous les templates associés (Admin uniquement)

    Args:
        collection_name: Nom de la collection à supprimer
        context: Contexte de la requête (vérifie les droits admin)

    Returns:
        Message de confirmation

    Raises:
        HTTPException: Si l'utilisateur n'est pas admin, si la collection n'existe pas ou si la suppression échoue
    """
    try:
        # Vérifier si la collection existe
        if not vector_store.collection_exists(collection_name):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Collection '{collection_name}' not found",
            )

        # Supprimer d'abord tous les templates associés à cette collection
        try:
            deleted_templates = template_table.delete_templates_by_group_id(collection_name)
            if deleted_templates:
                logger.info(
                    f"Deleted {len(deleted_templates)} templates associated with collection '{collection_name}' by admin user {context.user_id}"
                )
            else:
                logger.info(f"No templates found for collection '{collection_name}'")
        except Exception as template_error:
            logger.warning(f"Error deleting templates for collection '{collection_name}': {template_error}")
            # On continue même si la suppression des templates échoue

        # Supprimer la collection
        success = vector_store.delete_collection(collection_name)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete collection '{collection_name}'",
            )

        logger.info(f"Collection '{collection_name}' deleted successfully by admin user {context.user_id}")
        return MessageResponse(
            message=f"Collection '{collection_name}' and associated templates deleted successfully",
            success=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting collection '{collection_name}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
