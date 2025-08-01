from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
from src.schemas.vector import VectorSearchResult

from pydantic import BaseModel


class DistanceMetric(str, Enum):
    """Métriques de distance supportées par les vector stores"""

    COSINE = "Cosine"
    EUCLIDEAN = "Euclid"
    DOT = "Dot"
    MANHATTAN = "Manhattan"


@dataclass
class VectorPoint:
    """Représente un point vectoriel générique"""

    id: Union[str, int]
    vector: List[float]
    payload: Optional[Dict[str, Any]] = None


class CollectionInfo(BaseModel):
    """Informations sur une collection générique"""

    name: str
    vector_size: int
    distance_metric: str
    points_count: int
    status: str


class VectorStoreInterface(ABC):
    """Interface abstraite pour les vector stores"""

    # ===== GESTION DES COLLECTIONS =====

    @abstractmethod
    def create_collection(
        self, collection_name: str, vector_size: int, distance: DistanceMetric = DistanceMetric.COSINE, **kwargs
    ) -> bool:
        """
        Crée une nouvelle collection

        Args:
            collection_name: Nom de la collection
            vector_size: Taille des vecteurs
            distance: Métrique de distance
            **kwargs: Paramètres spécifiques au vector store

        Returns:
            True si la création réussit, False sinon
        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """
        Supprime une collection

        Args:
            collection_name: Nom de la collection à supprimer

        Returns:
            True si la suppression réussit, False sinon
        """
        pass

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        """
        Vérifie si une collection existe

        Args:
            collection_name: Nom de la collection

        Returns:
            True si la collection existe, False sinon
        """
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> Optional[CollectionInfo]:
        """
        Récupère les informations d'une collection

        Args:
            collection_name: Nom de la collection

        Returns:
            Informations de la collection ou None si erreur
        """
        pass

    @abstractmethod
    def list_collections(self) -> List[str]:
        """
        Liste toutes les collections

        Returns:
            Liste des noms de collections
        """
        pass

    # ===== GESTION DES POINTS =====

    @abstractmethod
    def upsert_points(self, collection_name: str, points: List[VectorPoint], wait: bool = True) -> bool:
        """
        Insert ou met à jour des points dans une collection

        Args:
            collection_name: Nom de la collection
            points: Liste des points à insérer/mettre à jour
            wait: Attendre la fin de l'opération

        Returns:
            True si l'opération réussit, False sinon
        """
        pass

    @abstractmethod
    def upsert_point(
        self,
        collection_name: str,
        point_id: Union[str, int],
        vector: List[float],
        payload: Optional[Dict[str, Any]] = None,
        wait: bool = True,
    ) -> bool:
        """
        Insert ou met à jour un point unique

        Args:
            collection_name: Nom de la collection
            point_id: ID du point
            vector: Vecteur du point
            payload: Métadonnées du point
            wait: Attendre la fin de l'opération

        Returns:
            True si l'opération réussit, False sinon
        """
        pass

    @abstractmethod
    def get_point(
        self,
        collection_name: str,
        point_id: Union[str, int],
        with_payload: bool = True,
        with_vector: bool = True,
    ) -> Optional[VectorPoint]:
        """
        Récupère un point par son ID

        Args:
            collection_name: Nom de la collection
            point_id: ID du point
            with_payload: Inclure les métadonnées
            with_vector: Inclure le vecteur

        Returns:
            Le point trouvé ou None
        """
        pass

    @abstractmethod
    def delete_points(self, collection_name: str, point_ids: List[Union[str, int]], wait: bool = True) -> bool:
        """
        Supprime des points par leurs IDs

        Args:
            collection_name: Nom de la collection
            point_ids: Liste des IDs à supprimer
            wait: Attendre la fin de l'opération

        Returns:
            True si la suppression réussit, False sinon
        """
        pass

    @abstractmethod
    def delete_point(self, collection_name: str, point_id: Union[str, int], wait: bool = True) -> bool:
        """
        Supprime un point par son ID

        Args:
            collection_name: Nom de la collection
            point_id: ID du point à supprimer
            wait: Attendre la fin de l'opération

        Returns:
            True si la suppression réussit, False sinon
        """
        pass

    @abstractmethod
    def delete_points_by_filter(
        self, collection_name: str, filter_conditions: Dict[str, Any], wait: bool = True
    ) -> bool:
        """
        Supprime des points selon des conditions de filtrage

        Args:
            collection_name: Nom de la collection
            filter_conditions: Conditions de filtrage
            wait: Attendre la fin de l'opération

        Returns:
            True si la suppression réussit, False sinon
        """
        pass

    # ===== RECHERCHE VECTORIELLE =====

    @abstractmethod
    def search_vectors(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        offset: int = 0,
        filter_conditions: Optional[Dict[str, Any]] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
        score_threshold: Optional[float] = None,
    ) -> List[VectorSearchResult]:
        """
        Recherche vectorielle dans une collection

        Args:
            collection_name: Nom de la collection
            query_vector: Vecteur de requête
            limit: Nombre maximum de résultats
            offset: Offset pour la pagination
            filter_conditions: Conditions de filtrage
            with_payload: Inclure les métadonnées
            with_vectors: Inclure les vecteurs
            score_threshold: Seuil de score minimum

        Returns:
            Liste des résultats de recherche
        """
        pass

    @abstractmethod
    def search_similar(
        self,
        collection_name: str,
        point_id: Union[str, int],
        limit: int = 10,
        filter_conditions: Optional[Dict[str, Any]] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
    ) -> List[VectorSearchResult]:
        """
        Recherche de points similaires à un point existant

        Args:
            collection_name: Nom de la collection
            point_id: ID du point de référence
            limit: Nombre maximum de résultats
            filter_conditions: Conditions de filtrage
            with_payload: Inclure les métadonnées
            with_vectors: Inclure les vecteurs

        Returns:
            Liste des résultats de recherche
        """
        pass

    # ===== UTILITAIRES =====

    @abstractmethod
    def count_points(self, collection_name: str) -> int:
        """
        Compte le nombre de points dans une collection

        Args:
            collection_name: Nom de la collection

        Returns:
            Nombre de points dans la collection
        """
        pass

    @abstractmethod
    def scroll_points(
        self,
        collection_name: str,
        limit: int = 100,
        offset: Optional[Union[str, int]] = None,
        with_payload: bool = True,
        with_vectors: bool = False,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> List[VectorPoint]:
        """
        Parcourt les points d'une collection avec pagination

        Args:
            collection_name: Nom de la collection
            limit: Nombre maximum de points à récupérer
            offset: Point de départ pour la pagination
            with_payload: Inclure les métadonnées
            with_vectors: Inclure les vecteurs
            filter_conditions: Conditions de filtrage

        Returns:
            Liste des points
        """
        pass

    @abstractmethod
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Récupère les statistiques d'une collection

        Args:
            collection_name: Nom de la collection

        Returns:
            Dictionnaire contenant les statistiques
        """
        pass
