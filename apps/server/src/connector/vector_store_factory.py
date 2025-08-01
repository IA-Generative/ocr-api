from typing import Optional, Dict, Any
from enum import Enum

from qdrant_client import QdrantClient

from .vector_store_interface import VectorStoreInterface
from .collection_manager import QdrantVectorStore


class VectorStoreType(str, Enum):
    """Types de vector stores supportés"""

    QDRANT = "qdrant"
    # Facilement extensible pour d'autres vector stores
    # CHROMA = "chroma"
    # PINECONE = "pinecone"
    # WEAVIATE = "weaviate"


class VectorStoreFactory:
    """Factory pour créer des instances de vector stores"""

    @staticmethod
    def create_vector_store(store_type: VectorStoreType, config: Dict[str, Any]) -> VectorStoreInterface:
        """
        Crée une instance de vector store selon le type spécifié

        Args:
            store_type: Type de vector store à créer
            config: Configuration pour le vector store

        Returns:
            Instance du vector store

        Raises:
            ValueError: Si le type de vector store n'est pas supporté
        """
        if store_type == VectorStoreType.QDRANT:
            return VectorStoreFactory._create_qdrant_store(config)

        # Extensible pour d'autres vector stores
        # elif store_type == VectorStoreType.CHROMA:
        #     return VectorStoreFactory._create_chroma_store(config)
        # elif store_type == VectorStoreType.PINECONE:
        #     return VectorStoreFactory._create_pinecone_store(config)

        else:
            raise ValueError(f"Vector store type '{store_type}' not supported")

    @staticmethod
    def _create_qdrant_store(config: Dict[str, Any]) -> QdrantVectorStore:
        """
        Crée une instance Qdrant

        Args:
            config: Configuration Qdrant avec les clés:
                - url: URL du serveur Qdrant (optionnel, défaut: localhost:6333)
                - api_key: Clé API (optionnel)
                - timeout: Timeout en secondes (optionnel, défaut: 60)

        Returns:
            Instance QdrantVectorStore
        """

        client = QdrantClient(**config)
        return QdrantVectorStore(client)


# Configuration par défaut pour différents vector stores
DEFAULT_CONFIGS = {
    VectorStoreType.QDRANT: {
        "url": "http://localhost:6333",
        "timeout": 60,
    },
    # VectorStoreType.CHROMA: {
    #     "persist_directory": "./chroma_db",
    # },
    # VectorStoreType.PINECONE: {
    #     "environment": "us-west1-gcp",
    # },
}


def create_default_vector_store(
    store_type: VectorStoreType = VectorStoreType.QDRANT,
    custom_config: Optional[Dict[str, Any]] = None,
) -> VectorStoreInterface:
    """
    Crée un vector store avec la configuration par défaut

    Args:
        store_type: Type de vector store à créer
        custom_config: Configuration personnalisée qui override les valeurs par défaut

    Returns:
        Instance du vector store configuré
    """
    config = DEFAULT_CONFIGS.get(store_type, {}).copy()

    if custom_config:
        config.update(custom_config)

    return VectorStoreFactory.create_vector_store(store_type, config)
