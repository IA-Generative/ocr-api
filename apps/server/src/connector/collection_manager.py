from typing import List, Optional, Dict, Any, Union

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    Match,
)

from src.logger import logger
from src.connector.vector_store_interface import (
    VectorStoreInterface,
    VectorPoint,
    DistanceMetric,
    CollectionInfo,
)
from src.schemas.vector import VectorSearchResult


class QdrantVectorStore(VectorStoreInterface):
    """Implémentation Qdrant du vector store"""

    def __init__(self, client: QdrantClient):
        self.client = client

    # ===== GESTION DES COLLECTIONS =====

    def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: DistanceMetric = DistanceMetric.COSINE,
        on_disk_payload: bool = True,
        replication_factor: int = 1,
        write_consistency_factor: int = 1,
        **kwargs,
    ) -> bool:
        """
        Crée une nouvelle collection

        Args:
            collection_name: Nom de la collection
            vector_size: Taille des vecteurs
            distance: Métrique de distance
            on_disk_payload: Stockage des payloads sur disque
            replication_factor: Facteur de réplication
            write_consistency_factor: Facteur de cohérence d'écriture

        Returns:
            True si la création réussit, False sinon
        """
        try:
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance(distance.value)),
                on_disk_payload=on_disk_payload,
                replication_factor=replication_factor,
                write_consistency_factor=write_consistency_factor,
            )
            logger.info(f"Collection '{collection_name}' créée avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la création de la collection '{collection_name}': {e}")
            return False

    def delete_collection(self, collection_name: str) -> bool:
        """
        Supprime une collection

        Args:
            collection_name: Nom de la collection à supprimer

        Returns:
            True si la suppression réussit, False sinon
        """
        if not self.collection_exists(collection_name):
            logger.warning(f"Collection '{collection_name}' n'existe pas, suppression ignorée")
            return False

        try:
            self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' supprimée avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la collection '{collection_name}': {e}")
            return False

    def collection_exists(self, collection_name: str) -> bool:
        """
        Vérifie si une collection existe

        Args:
            collection_name: Nom de la collection

        Returns:
            True si la collection existe, False sinon
        """
        try:
            collections = self.client.get_collections()
            return any(collection.name == collection_name for collection in collections.collections)
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'existence de la collection '{collection_name}': {e}")
            return False

    def get_collection_info(self, collection_name: str) -> Optional[CollectionInfo]:
        """
        Récupère les informations d'une collection

        Args:
            collection_name: Nom de la collection

        Returns:
            Informations de la collection ou None si erreur
        """
        try:
            qdrant_info = self.client.get_collection(collection_name=collection_name)
            return CollectionInfo(
                name=collection_name,
                vector_size=qdrant_info.config.params.vectors.size,
                distance_metric=qdrant_info.config.params.vectors.distance.value,
                points_count=self.count_points(collection_name),
                status=qdrant_info.status.value,
            )
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des infos de la collection '{collection_name}': {e}")
            return None

    def list_collections(self) -> List[str]:
        """
        Liste toutes les collections

        Returns:
            Liste des noms de collections
        """
        try:
            collections = self.client.get_collections()
            return [collection.name for collection in collections.collections]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la liste des collections: {e}")
            return []

    # ===== GESTION DES POINTS =====

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
        try:
            qdrant_points = [
                PointStruct(id=point.id, vector=point.vector, payload=point.payload or {}) for point in points
            ]

            result = self.client.upsert(collection_name=collection_name, points=qdrant_points, wait=wait)

            logger.info(f"Upsert de {len(points)} points dans la collection '{collection_name}' réussi")
            return result.status == "completed" if hasattr(result, "status") else True
        except Exception as e:
            logger.error(f"Erreur lors de l'upsert dans la collection '{collection_name}': {e}")
            return False

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
        point = VectorPoint(id=point_id, vector=vector, payload=payload)
        return self.upsert_points(collection_name, [point], wait)

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
        try:
            result = self.client.retrieve(
                collection_name=collection_name,
                ids=[point_id],
                with_payload=with_payload,
                with_vectors=with_vector,
            )

            if result:
                point = result[0]
                return VectorPoint(
                    id=point.id,
                    vector=point.vector if with_vector else None,
                    payload=point.payload if with_payload else None,
                )
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du point {point_id} dans '{collection_name}': {e}")
            return None

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
        try:
            self.client.delete(collection_name=collection_name, points_selector=point_ids, wait=wait)
            logger.info(f"Suppression de {len(point_ids)} points dans '{collection_name}' réussie")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de points dans '{collection_name}': {e}")
            return False

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
        return self.delete_points(collection_name, [point_id], wait)

    def delete_points_by_filter(
        self, collection_name: str, filter_conditions: Dict[str, Any], wait: bool = True
    ) -> bool:
        """
        Supprime des points selon des conditions de filtrage

        Args:
            collection_name: Nom de la collection
            filter_conditions: Conditions de filtrage (ex: {"category": "document"})
            wait: Attendre la fin de l'opération

        Returns:
            True si la suppression réussit, False sinon
        """
        try:
            conditions = [FieldCondition(key=key, match=Match(value=value)) for key, value in filter_conditions.items()]

            filter_obj = Filter(must=conditions)

            self.client.delete(collection_name=collection_name, points_selector=filter_obj, wait=wait)
            logger.info(f"Suppression par filtre dans '{collection_name}' réussie")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression par filtre dans '{collection_name}': {e}")
            return False

    # ===== RECHERCHE VECTORIELLE =====

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
        try:
            # Construction du filtre si nécessaire
            filter_obj = None
            if filter_conditions:
                conditions = [
                    FieldCondition(key=key, match=Match(value=value)) for key, value in filter_conditions.items()
                ]
                filter_obj = Filter(must=conditions)

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                offset=offset,
                query_filter=filter_obj,
                with_payload=with_payload,
                with_vectors=with_vectors,
                score_threshold=score_threshold,
            )

            search_results = []
            for result in results:
                search_results.append(
                    VectorSearchResult(
                        id=result.id,
                        score=result.score,
                        payload=result.payload if with_payload else None,
                        vector=result.vector if with_vectors else None,
                    )
                )

            logger.info(f"Recherche dans '{collection_name}' - {len(search_results)} résultats trouvés")
            return search_results

        except Exception as e:
            logger.error(f"Erreur lors de la recherche dans '{collection_name}': {e}")
            return []

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
        try:
            # Récupérer le vecteur du point de référence
            reference_point = self.get_point(collection_name, point_id, with_vector=True)
            if not reference_point or not reference_point.vector:
                logger.error(f"Point {point_id} non trouvé ou sans vecteur")
                return []

            # Effectuer la recherche
            return self.search_vectors(
                collection_name=collection_name,
                query_vector=reference_point.vector,
                limit=limit + 1,  # +1 pour exclure le point de référence
                filter_conditions=filter_conditions,
                with_payload=with_payload,
                with_vectors=with_vectors,
            )[1:]  # Exclure le premier résultat (le point lui-même)

        except Exception as e:
            logger.error(f"Erreur lors de la recherche de similarité dans '{collection_name}': {e}")
            return []

    # ===== UTILITAIRES =====

    def count_points(self, collection_name: str) -> int:
        """
        Compte le nombre de points dans une collection

        Args:
            collection_name: Nom de la collection

        Returns:
            Nombre de points dans la collection
        """
        try:
            result = self.client.count(collection_name=collection_name)
            return result.count
        except Exception as e:
            logger.error(f"Erreur lors du comptage des points dans '{collection_name}': {e}")
            return 0

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
        try:
            # Construction du filtre si nécessaire
            filter_obj = None
            if filter_conditions:
                conditions = [
                    FieldCondition(key=key, match=Match(value=value)) for key, value in filter_conditions.items()
                ]
                filter_obj = Filter(must=conditions)

            result = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                offset=offset,
                with_payload=with_payload,
                with_vectors=with_vectors,
                scroll_filter=filter_obj,
            )

            points = []
            for point in result[0]:  # result[0] contient les points, result[1] le next_page_offset
                points.append(
                    VectorPoint(
                        id=point.id,
                        vector=point.vector if with_vectors else None,
                        payload=point.payload if with_payload else None,
                    )
                )

            return points

        except Exception as e:
            logger.error(f"Erreur lors du parcours des points dans '{collection_name}': {e}")
            return []

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Récupère les statistiques d'une collection

        Args:
            collection_name: Nom de la collection

        Returns:
            Dictionnaire contenant les statistiques
        """
        try:
            info = self.get_collection_info(collection_name)
            count = self.count_points(collection_name)

            if info:
                return {
                    "name": collection_name,
                    "points_count": count,
                    "vector_size": info.vector_size,
                    "distance_metric": info.distance_metric,
                    "status": info.status,
                }
            return {"name": collection_name, "error": "Collection info not available"}

        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats de '{collection_name}': {e}")
            return {"name": collection_name, "error": str(e)}


# Instance globale (à initialiser avec le client Qdrant)
vector_store: Optional[VectorStoreInterface] = None


def get_vector_store() -> VectorStoreInterface:
    """Récupère l'instance du vector store"""
    global vector_store
    if vector_store is None:
        raise RuntimeError("VectorStore non initialisé. Appelez init_vector_store() d'abord.")
    return vector_store


def init_qdrant_vector_store(qdrant_client: QdrantClient) -> QdrantVectorStore:
    """Initialise le vector store avec un client Qdrant"""
    global vector_store
    vector_store = QdrantVectorStore(qdrant_client)
    return vector_store
