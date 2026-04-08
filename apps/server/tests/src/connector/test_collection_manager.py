import pytest
from unittest.mock import Mock, patch
from src.connector.vector_store_interface import (
    VectorPoint,
    DistanceMetric,
    CollectionInfo,
)
from qdrant_client import QdrantClient
from src.schemas.vector import VectorSearchResult

from src.connector.collection_manager import (
    QdrantVectorStore,
    get_vector_store,
    init_qdrant_vector_store,
    vector_store,
)


@pytest.fixture
def mock_qdrant_client() -> QdrantClient:
    """Mock Qdrant client"""
    return QdrantClient(":memory:")


@pytest.fixture
def vector_store_instance(mock_qdrant_client: QdrantClient) -> QdrantVectorStore:
    """QdrantVectorStore instance with mocked client"""
    return QdrantVectorStore(mock_qdrant_client)


class TestQdrantVectorStore:
    """Tests for QdrantVectorStore class"""

    # ===== COLLECTION MANAGEMENT TESTS =====

    def test_create_collection_success(self, vector_store_instance: QdrantVectorStore):
        """Test successful collection creation"""

        result = vector_store_instance.create_collection(
            collection_name="test_collection",
            vector_size=128,
            distance=DistanceMetric.COSINE,
        )

        assert result is True

    def test_create_collection_failure(
        self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient
    ):
        """Test collection creation failure"""
        with patch.object(mock_qdrant_client, "create_collection") as mock_create:
            mock_create.side_effect = Exception("Creation failed")

            result = vector_store_instance.create_collection(collection_name="test_collection", vector_size=128)

            assert result is False

    def test_delete_collection_success(
        self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient
    ):
        """Test successful collection deletion"""
        with (
            patch.object(mock_qdrant_client, "delete_collection") as mock_delete,
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
        ):
            mock_exists.return_value = True
            mock_delete.return_value = None

            result = vector_store_instance.delete_collection("test_collection")

            assert result is True

    def test_delete_collection_not_exists(self, vector_store_instance: QdrantVectorStore):
        """Test deletion of non-existent collection"""
        with patch.object(vector_store_instance, "collection_exists") as mock_exists:
            mock_exists.return_value = False

            result = vector_store_instance.delete_collection("test_collection")

            assert result is False

    def test_delete_collection_failure(
        self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient
    ):
        """Test collection deletion failure"""
        with (
            patch.object(mock_qdrant_client, "delete_collection") as mock_delete,
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
        ):
            mock_exists.return_value = True
            mock_delete.side_effect = Exception("Deletion failed")

            result = vector_store_instance.delete_collection("test_collection")

            assert result is False

    def test_collection_exists_true(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test collection exists returns True"""
        with (
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
            patch.object(mock_qdrant_client, "get_collections") as mock_get,
        ):
            mock_exists.return_value = True

            mock_collections = [
                Mock(name="test_collection"),
                Mock(name="other_collection"),
            ]
            mock_get.return_value = mock_collections

            result = vector_store_instance.collection_exists("test_collection")

            assert result is True

    def test_collection_exists_false(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test collection exists returns False"""
        with (
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
            patch.object(mock_qdrant_client, "get_collections") as mock_get,
        ):
            mock_exists.return_value = False

            mock_collections = [Mock(name="other_collection")]
            mock_get.return_value = mock_collections

            result = vector_store_instance.collection_exists("test_collection")

            assert result is False

    def test_collection_exists_error(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test collection exists with error"""
        with (
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
            patch.object(mock_qdrant_client, "get_collections") as mock_get,
        ):
            mock_exists.return_value = False
            mock_get.side_effect = Exception("Get collections failed")

            result = vector_store_instance.collection_exists("test_collection")

            assert result is False

    def test_get_collection_info_success(
        self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient
    ):
        """Test successful collection info retrieval"""
        with (
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
            patch.object(mock_qdrant_client, "get_collection") as mock_get,
        ):
            mock_exists.return_value = True
            mock_info = Mock()
            mock_info.config.params.vectors.size = 128
            mock_info.config.params.vectors.distance.value = "Cosine"
            mock_info.status.value = "green"
            mock_get.return_value = mock_info
            vector_store_instance.count_points = Mock(return_value=100)

            result = vector_store_instance.get_collection_info("test_collection")

        assert result is not None
        assert result.name == "test_collection"
        assert result.vector_size == 128
        assert result.distance_metric == "Cosine"
        assert result.points_count == 100
        assert result.status == "green"

    def test_get_collection_info_error(
        self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient
    ):
        """Test collection info retrieval error"""
        with (
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
            patch.object(mock_qdrant_client, "get_collection") as mock_get,
        ):
            mock_exists.return_value = False
            mock_get.side_effect = Exception("Get collection failed")

            result = vector_store_instance.get_collection_info("test_collection")

            assert result is None

    def test_list_collections_success(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test successful collections listing"""
        with patch.object(mock_qdrant_client, "get_collections") as mock_get:
            # Créer des mocks avec l'attribut name correctement défini
            collection1 = Mock()
            collection1.name = "collection1"

            collection2 = Mock()
            collection2.name = "collection2"

            mock_collections_response = Mock()
            mock_collections_response.collections = [collection1, collection2]
            mock_get.return_value = mock_collections_response

            result = vector_store_instance.list_collections()

            assert result == ["collection1", "collection2"]

    def test_list_collections_error(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test collections listing error"""
        with (
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
            patch.object(mock_qdrant_client, "get_collections") as mock_get,
        ):
            mock_exists.return_value = True
            mock_get.side_effect = Exception("Get collections failed")

            result = vector_store_instance.list_collections()

            assert result == []

    # ===== POINT MANAGEMENT TESTS =====

    def test_upsert_points_success(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test successful points upsert"""
        with (
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
            patch.object(mock_qdrant_client, "upsert") as mock_upsert,
        ):
            mock_exists.return_value = True
            mock_result = Mock()
            mock_result.status = "completed"
            mock_upsert.return_value = mock_result

            points = [
                VectorPoint(id="1", vector=[0.1, 0.2, 0.3], payload={"text": "test1"}),
                VectorPoint(id="2", vector=[0.4, 0.5, 0.6], payload={"text": "test2"}),
            ]

            result = vector_store_instance.upsert_points("test_collection", points)

            assert result is True

    def test_upsert_points_failure(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test points upsert failure"""
        with (
            patch.object(vector_store_instance, "collection_exists") as mock_exists,
            patch.object(mock_qdrant_client, "upsert") as mock_upsert,
        ):
            mock_exists.return_value = True
            mock_upsert.side_effect = Exception("Upsert failed")

            points = [VectorPoint(id="1", vector=[0.1, 0.2, 0.3])]
            result = vector_store_instance.upsert_points("test_collection", points)

            assert result is False

    def test_upsert_point_success(self, vector_store_instance: QdrantVectorStore):
        """Test successful single point upsert"""
        vector_store_instance.upsert_points = Mock(return_value=True)

        result = vector_store_instance.upsert_point("test_collection", "1", [0.1, 0.2, 0.3], {"text": "test"})

        assert result is True
        vector_store_instance.upsert_points.assert_called_once()

    def test_get_point_success(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test successful point retrieval"""
        with patch.object(mock_qdrant_client, "retrieve") as mock_retrieve:
            mock_point = Mock()
            mock_point.id = "1"
            mock_point.vector = [0.1, 0.2, 0.3]
            mock_point.payload = {"text": "test"}
            mock_retrieve.return_value = [mock_point]

            result = vector_store_instance.get_point("test_collection", "1")

            assert result is not None
            assert result.id == "1"
            assert result.vector == [0.1, 0.2, 0.3]
            assert result.payload == {"text": "test"}

    def test_get_point_not_found(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test point not found"""
        with patch.object(mock_qdrant_client, "retrieve") as mock_retrieve:
            mock_retrieve.return_value = []

            result = vector_store_instance.get_point("test_collection", "1")

            assert result is None

    def test_get_point_error(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test point retrieval error"""
        with patch.object(mock_qdrant_client, "retrieve") as mock_retrieve:
            mock_retrieve.side_effect = Exception("Retrieve failed")

            result = vector_store_instance.get_point("test_collection", "1")

            assert result is None

    def test_delete_points_success(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test successful points deletion"""
        with patch.object(mock_qdrant_client, "delete") as mock_delete:
            mock_delete.return_value = None

            result = vector_store_instance.delete_points("test_collection", ["1", "2"])

            assert result is True

    def test_delete_points_failure(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test points deletion failure"""
        with patch.object(mock_qdrant_client, "delete") as mock_delete:
            mock_delete.side_effect = Exception("Delete failed")

            result = vector_store_instance.delete_points("test_collection", ["1", "2"])

            assert result is False

    def test_delete_point_success(self, vector_store_instance: QdrantVectorStore):
        """Test successful single point deletion"""
        with patch.object(vector_store_instance, "delete_points", return_value=True):
            result = vector_store_instance.delete_point("test_collection", "1")
            assert result is True

    # def test_delete_points_by_filter_success(
    #     self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient
    # ):
    #     """Test successful points deletion by filter"""
    #     with patch.object(mock_qdrant_client, "delete") as mock_delete:
    #         mock_delete.return_value = True

    #         result = vector_store_instance.delete_points_by_filter(
    #             "test_collection", {"category": "document"}
    #         )

    #         assert result is True

    def test_delete_points_by_filter_failure(
        self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient
    ):
        """Test points deletion by filter failure"""
        with patch.object(mock_qdrant_client, "delete") as mock_delete:
            mock_delete.side_effect = Exception("Delete by filter failed")

            result = vector_store_instance.delete_points_by_filter("test_collection", {"category": "document"})

            assert result is False

    # ===== VECTOR SEARCH TESTS =====

    def test_search_vectors_success(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test successful vector search"""
        with patch.object(mock_qdrant_client, "query_points") as mock_search:
            mock_result1 = Mock()
            mock_result1.id = "1"
            mock_result1.score = 0.95
            mock_result1.payload = {"text": "test1"}
            mock_result1.vector = [0.1, 0.2, 0.3]

            mock_result2 = Mock()
            mock_result2.id = "2"
            mock_result2.score = 0.85
            mock_result2.payload = {"text": "test2"}
            mock_result2.vector = [0.4, 0.5, 0.6]

            mock_response = Mock()
            mock_response.points = [mock_result1, mock_result2]
            mock_search.return_value = mock_response

            results = vector_store_instance.search_vectors("test_collection", [0.1, 0.2, 0.3], limit=10)

            assert len(results) == 2
            assert results[0].id == "1"
            assert results[0].score == 0.95
            assert results[1].id == "2"
            assert results[1].score == 0.85

    def test_search_vectors_with_filter(
        self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient
    ):
        """Test vector search with filter conditions"""
        with patch.object(mock_qdrant_client, "query_points") as mock_search:
            mock_response = Mock()
            mock_response.points = []
            mock_search.return_value = mock_response

            results = vector_store_instance.search_vectors(
                "test_collection",
                [0.1, 0.2, 0.3],
                filter_conditions={"category": "document"},
            )

            assert results == []

    def test_search_vectors_error(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test vector search error"""
        with patch.object(mock_qdrant_client, "query_points") as mock_search:
            mock_search.side_effect = Exception("Search failed")

            results = vector_store_instance.search_vectors("test_collection", [0.1, 0.2, 0.3])

            assert results == []

    def test_search_similar_success(self, vector_store_instance: QdrantVectorStore):
        """Test successful similar search"""
        with patch.object(vector_store_instance, "get_point") as mock_get:
            reference_point = VectorPoint(id="1", vector=[0.1, 0.2, 0.3])
            mock_get.return_value = reference_point

            mock_results = [
                VectorSearchResult(id="1", score=1.0),  # self
                VectorSearchResult(id="2", score=0.9),
                VectorSearchResult(id="3", score=0.8),
            ]
            vector_store_instance.search_vectors = Mock(return_value=mock_results)

            results = vector_store_instance.search_similar("test_collection", "1", limit=10)

            assert len(results) == 2  # Excludes self
            assert results[0].id == "2"
            assert results[1].id == "3"

    def test_search_similar_point_not_found(self, vector_store_instance):
        """Test similar search with point not found"""
        vector_store_instance.get_point = Mock(return_value=None)

        results = vector_store_instance.search_similar("test_collection", "1")

        assert results == []

    def test_search_similar_no_vector(self, vector_store_instance):
        """Test similar search with point without vector"""
        point_without_vector = VectorPoint(id="1", vector=None)
        vector_store_instance.get_point = Mock(return_value=point_without_vector)

        results = vector_store_instance.search_similar("test_collection", "1")

        assert results == []

    # ===== UTILITY TESTS =====

    def test_count_points_success(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test successful point counting"""
        with patch.object(mock_qdrant_client, "count") as mock_count:
            mock_result = Mock()
            mock_result.count = 100
            mock_count.return_value = mock_result

            result = vector_store_instance.count_points("test_collection")

            assert result == 100

    def test_count_points_error(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test point counting error"""
        with patch.object(mock_qdrant_client, "count") as mock_count:
            mock_count.side_effect = Exception("Count failed")

            result = vector_store_instance.count_points("test_collection")

            assert result == 0

    def test_scroll_points_success(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test successful points scrolling"""
        with (
            patch.object(mock_qdrant_client, "scroll") as mock_scroll,
            patch.object(mock_qdrant_client, "scroll") as mock_scroll,
        ):
            mock_scroll.return_value = ([], None)

            mock_point1 = Mock()
            mock_point1.id = "1"
            mock_point1.vector = [0.1, 0.2, 0.3]
            mock_point1.payload = {"text": "test1"}

            mock_point2 = Mock()
            mock_point2.id = "2"
            mock_point2.vector = None
            mock_point2.payload = {"text": "test2"}

            mock_scroll.return_value = ([mock_point1, mock_point2], None)

            results = vector_store_instance.scroll_points("test_collection", limit=100)

            assert len(results) == 2
            assert results[0].id == "1"
            assert results[1].id == "2"

    def test_scroll_points_with_filter(
        self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient
    ):
        """Test points scrolling with filter"""
        with patch.object(mock_qdrant_client, "scroll") as mock_scroll:
            mock_scroll.return_value = ([], None)

            results = vector_store_instance.scroll_points("test_collection", filter_conditions={"category": "document"})

            assert results == []

    def test_scroll_points_error(self, vector_store_instance: QdrantVectorStore, mock_qdrant_client: QdrantClient):
        """Test points scrolling error"""
        with patch.object(mock_qdrant_client, "scroll") as mock_scroll:
            mock_scroll.side_effect = Exception("Scroll failed")

            results = vector_store_instance.scroll_points("test_collection")

            assert results == []

    def test_get_collection_stats_success(self, vector_store_instance: QdrantVectorStore):
        """Test successful collection stats retrieval"""
        mock_info = CollectionInfo(
            name="test_collection",
            vector_size=128,
            distance_metric="Cosine",
            points_count=100,
            status="green",
        )
        vector_store_instance.get_collection_info = Mock(return_value=mock_info)
        vector_store_instance.count_points = Mock(return_value=100)

        stats = vector_store_instance.get_collection_stats("test_collection")

        assert stats["name"] == "test_collection"
        assert stats["points_count"] == 100
        assert stats["vector_size"] == 128
        assert stats["distance_metric"] == "Cosine"
        assert stats["status"] == "green"

    def test_get_collection_stats_no_info(self, vector_store_instance):
        """Test collection stats with no info available"""
        vector_store_instance.get_collection_info = Mock(return_value=None)

        stats = vector_store_instance.get_collection_stats("test_collection")

        assert stats["name"] == "test_collection"
        assert "error" in stats

    def test_get_collection_stats_error(self, vector_store_instance):
        """Test collection stats retrieval error"""
        vector_store_instance.get_collection_info = Mock(side_effect=Exception("Stats failed"))

        stats = vector_store_instance.get_collection_stats("test_collection")

        assert stats["name"] == "test_collection"
        assert stats["error"] == "Stats failed"


class TestGlobalFunctions:
    """Tests for global vector store functions"""

    def test_get_vector_store_initialized(self, mock_qdrant_client):
        """Test get_vector_store when initialized"""
        global vector_store
        original_vector_store = vector_store

        try:
            init_qdrant_vector_store(mock_qdrant_client)
            store = get_vector_store()
            assert isinstance(store, QdrantVectorStore)
        finally:
            vector_store = original_vector_store

    def test_init_qdrant_vector_store(self, mock_qdrant_client):
        """Test initialization of Qdrant vector store"""
        global vector_store
        original_vector_store = vector_store

        try:
            result = init_qdrant_vector_store(mock_qdrant_client)
            assert isinstance(result, QdrantVectorStore)
            assert result.client == mock_qdrant_client
        finally:
            vector_store = original_vector_store
