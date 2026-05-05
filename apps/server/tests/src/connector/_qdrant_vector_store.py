import pytest
from qdrant_client import QdrantClient
from uuid import uuid4

from src.connector.collection_manager import QdrantVectorStore
from src.connector.vector_store_interface import (
    VectorPoint,
    DistanceMetric,
)


@pytest.fixture(scope="function")
def mock_qdrant_client() -> QdrantClient:
    """Mock du client Qdrant"""
    return QdrantClient(":memory:")


@pytest.fixture
def qdrant_store(mock_qdrant_client: QdrantClient) -> QdrantVectorStore:
    """Instance QdrantVectorStore avec mock client"""
    return QdrantVectorStore(mock_qdrant_client)


def test_init(mock_qdrant_client: QdrantClient):
    """Test initialisation"""
    store = QdrantVectorStore(mock_qdrant_client)
    assert store.client == mock_qdrant_client


def test_create_collection_success(qdrant_store: QdrantVectorStore):
    """Test création de collection réussie"""

    result = qdrant_store.create_collection("test_collection", 128)

    assert result is True


def test_create_collection_with_custom_params(qdrant_store: QdrantVectorStore):
    """Test création avec paramètres personnalisés"""

    result = qdrant_store.create_collection(
        "test_collection",
        256,
        distance=DistanceMetric.EUCLIDEAN,
        on_disk_payload=False,
        replication_factor=2,
    )

    assert result is True


def test_delete_collection_success(qdrant_store: QdrantVectorStore):
    """Test suppression de collection réussie"""

    qdrant_store.create_collection("test_collection", 128)

    result = qdrant_store.delete_collection("test_collection")

    assert result is True


def test_delete_collection_failure(qdrant_store: QdrantVectorStore):
    """Test échec suppression de collection"""

    result = qdrant_store.delete_collection("test_collectionsqsqsqs")

    assert result is False


def test_collection_exists_true(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test vérification existence collection (existe)"""
    qdrant_store.create_collection("test_collection", 128)

    result = qdrant_store.collection_exists("test_collection")

    assert result is True


def test_collection_exists_false(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test vérification existence collection (n'existe pas)"""

    result = qdrant_store.collection_exists("test_collection")

    assert result is False


def test_get_collection_info_success(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test récupération infos collection réussie"""
    # Mock de la réponse Qdrant
    qdrant_store.create_collection("test_collection", 128)

    result = qdrant_store.get_collection_info("test_collection")

    assert result is not None
    assert result.name == "test_collection"
    assert result.vector_size == 128
    assert result.distance_metric == "Cosine"
    assert result.status == "green"


def test_get_collection_info_failure(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test échec récupération infos collection"""

    result = qdrant_store.get_collection_info("test_collection")

    assert result is None


def test_list_collections(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test listage des collections"""
    qdrant_store.create_collection("collection1", 128)
    qdrant_store.create_collection("collection2", 128)

    result = qdrant_store.list_collections()

    assert result == ["collection1", "collection2"]


def test_list_collections_error(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test erreur lors du listage"""
    result = qdrant_store.list_collections()

    assert result == []


def test_upsert_points_success(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test insertion points réussie"""
    qdrant_store.create_collection("test_collection", 3)

    points = [
        VectorPoint(id=str(uuid4()), vector=[1.0, 2.0, 3.0], payload={"cat": "A"}),
        VectorPoint(id=str(uuid4()), vector=[4.0, 5.0, 6.0], payload={"cat": "B"}),
    ]

    result = qdrant_store.upsert_points("test_collection", points)

    assert result is True


def test_upsert_points_failure(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test échec insertion points"""

    points = [VectorPoint(id=str(uuid4()), vector=[1.0, 2.0, 3.0])]
    result = qdrant_store.upsert_points("test_collection", points)

    assert result is False


def test_upsert_point(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test insertion point unique"""
    qdrant_store.create_collection("test_collection", 3)

    result = qdrant_store.upsert_point("test_collection", str(uuid4()), [1.0, 2.0, 3.0], {"category": "test"})

    assert result is True


def test_get_point_success(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test récupération point réussie"""
    qdrant_store.create_collection("test_collection", 3)
    uuid = str(uuid4())
    qdrant_store.upsert_point("test_collection", uuid, [1.0, 2.0, 3.0], {"category": "test"})

    result = qdrant_store.get_point("test_collection", uuid)

    assert result is not None
    assert result.id == uuid
    assert result.payload["category"] == "test"


def test_get_point_not_found(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test récupération point inexistant"""

    result = qdrant_store.get_point("test_collection", str(uuid4()))

    assert result is None


def test_delete_points_success(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test suppression points réussie"""
    qdrant_store.create_collection("test_collection", 3)
    uuid = str(uuid4())
    qdrant_store.upsert_point("test_collection", uuid, [1.0, 2.0, 3.0], {"category": "test"})

    result = qdrant_store.delete_points("test_collection", [uuid])

    assert result is True
    result = qdrant_store.get_point("test_collection", uuid)

    assert result is None


def test_delete_points_failure(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    qdrant_store.create_collection("test_collection", 3)

    result = qdrant_store.delete_points("test_collection", [str(uuid4())])

    assert result is True


def test_delete_point(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test suppression point unique"""
    qdrant_store.create_collection("test_collection", 3)

    result = qdrant_store.delete_point("test_collection", "p1")

    assert result is True


def test_search_vectors_success(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test recherche vectorielle réussie"""
    # Mock des résultats de recherche
    qdrant_store.create_collection("test_collection", 3)
    uuid1 = str(uuid4())
    qdrant_store.upsert_point("test_collection", uuid1, [1.0, 1.0, 1.0], {"category": "test"})
    uuid2 = str(uuid4())
    qdrant_store.upsert_point("test_collection", uuid2, [1.0, 1.0, 3.0], {"category": "test"})

    results = qdrant_store.search_vectors(
        "test_collection",
        [1.0, 1.0, 1.0],
        limit=2,
        with_payload=True,
        with_vectors=True,
    )

    assert len(results) == 2
    assert results[0].id == uuid1
    assert results[0].score >= 1
    assert results[0].payload["category"] == "test"


def test_search_vectors_error(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test erreur recherche vectorielle"""
    qdrant_store.create_collection("test_collection", 3)
    results = qdrant_store.search_vectors("test_collection", [1.0, 1.0, 1.0])

    assert results == []


def test_search_similar_success(qdrant_store: QdrantVectorStore, mock_qdrant_client: QdrantClient):
    """Test recherche similarité réussie"""
    # Mock du point de référence
    qdrant_store.create_collection("test_collection", 3)
    uuid1 = str(uuid4())
    qdrant_store.upsert_point("test_collection", uuid1, [1.0, 1.0, 1.0], {"category": "test"})

    uuid2 = str(uuid4())
    qdrant_store.upsert_point("test_collection", uuid2, [1.0, 1.0, 10.0], {"category": "test"})
    uuid3 = str(uuid4())
    qdrant_store.upsert_point("test_collection", uuid3, [1.0, 1.0, 0.9], {"category": "test"})
    results = qdrant_store.search_similar("test_collection", uuid1, limit=1)

    # Le point de référence doit être exclu
    assert len(results) == 1
    assert results[0].id == uuid3
