"""
Tests unitaires pour VectorStoreFactory
"""

import pytest
from unittest.mock import Mock, patch

from src.connector.vector_store_factory import (
    VectorStoreFactory,
    VectorStoreType,
    create_default_vector_store,
    DEFAULT_CONFIGS,
)
from src.connector.collection_manager import QdrantVectorStore
from src.connector.vector_store_interface import VectorStoreInterface


class TestVectorStoreFactory:
    """Tests pour VectorStoreFactory"""

    @patch("src.connector.vector_store_factory.QdrantClient")
    def test_create_qdrant_store_default_config(self, mock_qdrant_client_class):
        """Test création Qdrant avec config par défaut"""
        mock_client = Mock()
        mock_qdrant_client_class.return_value = mock_client

        config = {"url": "http://localhost:6333", "timeout": 60}

        store = VectorStoreFactory.create_vector_store(VectorStoreType.QDRANT, config)

        assert isinstance(store, QdrantVectorStore)
        assert store.client == mock_client

        mock_qdrant_client_class.assert_called_once_with(url="http://localhost:6333", timeout=60)

    @patch("src.connector.vector_store_factory.QdrantClient")
    def test_create_qdrant_store_with_api_key(self, mock_qdrant_client_class):
        """Test création Qdrant avec clé API"""
        mock_client = Mock()
        mock_qdrant_client_class.return_value = mock_client

        config = {
            "url": "http://qdrant-server:6333",
            "timeout": 120,
            "api_key": "secret-key",
        }

        store = VectorStoreFactory.create_vector_store(VectorStoreType.QDRANT, config)

        assert isinstance(store, QdrantVectorStore)

        mock_qdrant_client_class.assert_called_once_with(
            url="http://qdrant-server:6333", timeout=120, api_key="secret-key"
        )

    def test_create_unsupported_vector_store(self):
        """Test création vector store non supporté"""
        with pytest.raises(ValueError, match="Vector store type 'invalid' not supported"):
            VectorStoreFactory.create_vector_store("invalid", {})

    @patch("src.connector.vector_store_factory.QdrantClient")
    def test_create_default_vector_store_qdrant(self, mock_qdrant_client_class):
        """Test création avec fonction de convenience"""
        mock_client = Mock()
        mock_qdrant_client_class.return_value = mock_client

        store = create_default_vector_store(VectorStoreType.QDRANT)

        assert isinstance(store, QdrantVectorStore)
        assert isinstance(store, VectorStoreInterface)

        # Vérifier que la config par défaut a été utilisée
        expected_config = DEFAULT_CONFIGS[VectorStoreType.QDRANT]
        mock_qdrant_client_class.assert_called_once_with(**expected_config)

    @patch("src.connector.vector_store_factory.QdrantClient")
    def test_create_default_vector_store_with_custom_config(self, mock_qdrant_client_class):
        """Test création avec config personnalisée"""
        mock_client = Mock()
        mock_qdrant_client_class.return_value = mock_client

        custom_config = {"timeout": 180, "api_key": "custom-key"}

        store = create_default_vector_store(VectorStoreType.QDRANT, custom_config)

        assert isinstance(store, QdrantVectorStore)

        # La config custom doit override la config par défaut
        mock_qdrant_client_class.assert_called_once_with(
            url="http://localhost:6333",  # Valeur par défaut
            timeout=180,  # Valeur custom
            api_key="custom-key",  # Valeur custom
        )

    def test_default_configs_exist(self):
        """Test que les configs par défaut existent"""
        assert VectorStoreType.QDRANT in DEFAULT_CONFIGS

        qdrant_config = DEFAULT_CONFIGS[VectorStoreType.QDRANT]
        assert "url" in qdrant_config
        assert "timeout" in qdrant_config
        assert qdrant_config["url"] == "http://localhost:6333"
        assert qdrant_config["timeout"] == 60

    def test_vector_store_type_enum(self):
        """Test enum VectorStoreType"""
        assert VectorStoreType.QDRANT == "qdrant"
        # Vérifier que l'enum est bien défini
        assert isinstance(VectorStoreType.QDRANT, str)


class TestVectorStoreFactoryIntegration:
    """Tests d'intégration pour VectorStoreFactory"""

    @patch("src.connector.vector_store_factory.QdrantClient")
    def test_factory_with_different_configs(self, mock_qdrant_client_class):
        """Test factory avec différentes configurations"""
        mock_client = Mock()
        mock_qdrant_client_class.return_value = mock_client

        configs = [
            {"url": "http://localhost:6333", "timeout": 30},
            {"url": "http://qdrant-prod:6333", "timeout": 120, "api_key": "prod-key"},
            {"url": "http://qdrant-dev:6333", "timeout": 60},
        ]

        stores = []
        for config in configs:
            store = VectorStoreFactory.create_vector_store(VectorStoreType.QDRANT, config)
            stores.append(store)
            assert isinstance(store, QdrantVectorStore)

        # Vérifier que 3 clients différents ont été créés
        assert mock_qdrant_client_class.call_count == 3

        # Vérifier les différents appels
        calls = mock_qdrant_client_class.call_args_list
        assert calls[0][1]["url"] == "http://localhost:6333"
        assert calls[1][1]["url"] == "http://qdrant-prod:6333"
        assert calls[1][1]["api_key"] == "prod-key"
        assert calls[2][1]["url"] == "http://qdrant-dev:6333"
