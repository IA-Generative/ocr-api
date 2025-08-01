import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, status
from src.connector.vector_store_interface import DistanceMetric, CollectionInfo
from ocr_backend.core.security.token import RequestContext

from ocr_backend.routers.collections import (
    verify_admin_access,
    create_collection,
    list_collections,
    get_collection,
    get_collection_stats,
    delete_collection,
    CollectionCreateRequest,
    CollectionResponse,
    CollectionStatsResponse,
    MessageResponse,
)


@pytest.fixture
def mock_vector_store():
    """Mock vector store"""
    return Mock()


@pytest.fixture
def mock_template_table():
    """Mock template table"""
    return Mock()


@pytest.fixture
def admin_context() -> RequestContext:
    """Mock admin request context"""
    context: RequestContext = Mock(spec=RequestContext)
    context.is_admin = True
    context.user_id = "admin_user_123"
    return context


@pytest.fixture
def user_context() -> RequestContext:
    """Mock regular user request context"""
    context: RequestContext = Mock(spec=RequestContext)
    context.is_admin = False
    context.user_id = "user_123"
    context.groups = ["group1", "group2"]
    return context


@pytest.fixture
def collection_create_request() -> CollectionCreateRequest:
    """Sample collection create request"""
    return CollectionCreateRequest(
        name="test_collection",
        vector_size=128,
        distance=DistanceMetric.COSINE,
        on_disk_payload=True,
        replication_factor=1,
        write_consistency_factor=1,
    )


class TestVerifyAdminAccess:
    """Tests for verify_admin_access function"""

    def test_verify_admin_access_success(self, admin_context: RequestContext):
        """Test successful admin verification"""
        result = verify_admin_access(admin_context)
        assert result == admin_context

    def test_verify_admin_access_forbidden(self, user_context: RequestContext):
        """Test admin verification with non-admin user"""
        with pytest.raises(HTTPException) as exc_info:
            verify_admin_access(user_context)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Admin access required" in exc_info.value.detail


class TestCreateCollection:
    """Tests for create_collection endpoint"""

    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_create_collection_success(
        self,
        mock_logger,
        mock_vector_store,
        collection_create_request: CollectionCreateRequest,
        admin_context: RequestContext,
    ):
        """Test successful collection creation"""
        mock_vector_store.collection_exists.return_value = False
        mock_vector_store.create_collection.return_value = True

        result = await create_collection(collection_create_request, admin_context)

        assert result.success is True
        assert "created successfully" in result.message
        mock_vector_store.collection_exists.assert_called_once_with("test_collection")
        mock_vector_store.create_collection.assert_called_once()
        mock_logger.info.assert_called_once()

    @patch("ocr_backend.routers.collections.vector_store")
    async def test_create_collection_already_exists(self, mock_vector_store, collection_create_request, admin_context):
        """Test creation when collection already exists"""
        mock_vector_store.collection_exists.return_value = True

        with pytest.raises(HTTPException) as exc_info:
            await create_collection(collection_create_request, admin_context)

        assert exc_info.value.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in exc_info.value.detail

    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_create_collection_creation_fails(
        self, mock_logger, mock_vector_store, collection_create_request, admin_context
    ):
        """Test creation failure from vector store"""
        mock_vector_store.collection_exists.return_value = False
        mock_vector_store.create_collection.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await create_collection(collection_create_request, admin_context)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to create collection" in exc_info.value.detail

    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_create_collection_exception(
        self, mock_logger, mock_vector_store, collection_create_request, admin_context
    ):
        """Test creation with unexpected exception"""
        mock_vector_store.collection_exists.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await create_collection(collection_create_request, admin_context)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Internal server error" in exc_info.value.detail
        mock_logger.error.assert_called_once()


class TestListCollections:
    """Tests for list_collections endpoint"""

    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_list_collections_admin(self, mock_logger, mock_vector_store, admin_context):
        """Test listing collections as admin"""
        mock_collections = ["collection1", "collection2", "collection3"]
        mock_vector_store.list_collections.return_value = mock_collections

        result = await list_collections(admin_context)

        assert result == mock_collections
        mock_logger.info.assert_called_once()

    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_list_collections_regular_user(self, mock_logger, mock_vector_store, user_context):
        """Test listing collections as regular user"""
        mock_collections = ["group1", "group2", "group3", "other_group"]
        mock_vector_store.list_collections.return_value = mock_collections

        result = await list_collections(user_context)

        # User should only see collections matching their groups
        assert result == ["group1", "group2"]
        mock_logger.info.assert_called_once()

    @patch("ocr_backend.routers.collections.vector_store")
    async def test_list_collections_user_no_groups(self, mock_vector_store):
        """Test listing collections for user with no groups"""
        context = Mock(spec=RequestContext)
        context.is_admin = False
        context.user_id = "user_123"
        # No groups attribute

        mock_collections = ["collection1", "collection2"]
        mock_vector_store.list_collections.return_value = mock_collections

        result = await list_collections(context)

        assert result == []

    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_list_collections_exception(self, mock_logger, mock_vector_store, admin_context):
        """Test listing collections with exception"""
        mock_vector_store.list_collections.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await list_collections(admin_context)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to list collections" in exc_info.value.detail
        mock_logger.error.assert_called_once()


class TestGetCollection:
    """Tests for get_collection endpoint"""

    @patch("ocr_backend.routers.collections.vector_store")
    async def test_get_collection_success(self, mock_vector_store, admin_context):
        """Test successful collection retrieval"""
        mock_vector_store.collection_exists.return_value = True
        mock_info = CollectionInfo(
            name="test_collection",
            vector_size=128,
            distance_metric="Cosine",
            points_count=100,
            status="green",
        )
        mock_vector_store.get_collection_info.return_value = mock_info

        result = await get_collection("test_collection", admin_context)

        assert isinstance(result, CollectionResponse)
        assert result.name == "test_collection"
        assert result.vector_size == 128
        assert result.distance_metric == "Cosine"
        assert result.points_count == 100
        assert result.status == "green"

    @patch("ocr_backend.routers.collections.vector_store")
    async def test_get_collection_not_found(self, mock_vector_store, admin_context):
        """Test getting non-existent collection"""
        mock_vector_store.collection_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await get_collection("nonexistent", admin_context)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail

    @patch("ocr_backend.routers.collections.vector_store")
    async def test_get_collection_info_fails(self, mock_vector_store, admin_context):
        """Test when collection info retrieval fails"""
        mock_vector_store.collection_exists.return_value = True
        mock_vector_store.get_collection_info.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await get_collection("test_collection", admin_context)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to retrieve collection" in exc_info.value.detail

    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_get_collection_exception(self, mock_logger, mock_vector_store, admin_context):
        """Test getting collection with exception"""
        mock_vector_store.collection_exists.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await get_collection("test_collection", admin_context)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Internal server error" in exc_info.value.detail
        mock_logger.error.assert_called_once()


class TestGetCollectionStats:
    """Tests for get_collection_stats endpoint"""

    @patch("ocr_backend.routers.collections.vector_store")
    async def test_get_collection_stats_success(self, mock_vector_store, admin_context):
        """Test successful collection stats retrieval"""
        mock_vector_store.collection_exists.return_value = True
        mock_stats = {
            "name": "test_collection",
            "points_count": 100,
            "vector_size": 128,
            "distance_metric": "Cosine",
            "status": "green",
        }
        mock_vector_store.get_collection_stats.return_value = mock_stats

        result = await get_collection_stats("test_collection", admin_context)

        assert isinstance(result, CollectionStatsResponse)
        assert result.name == "test_collection"
        assert result.points_count == 100
        assert result.vector_size == 128

    @patch("ocr_backend.routers.collections.vector_store")
    async def test_get_collection_stats_not_found(self, mock_vector_store, admin_context):
        """Test getting stats for non-existent collection"""
        mock_vector_store.collection_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await get_collection_stats("nonexistent", admin_context)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail

    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_get_collection_stats_exception(self, mock_logger, mock_vector_store, admin_context):
        """Test getting collection stats with exception"""
        mock_vector_store.collection_exists.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await get_collection_stats("test_collection", admin_context)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Internal server error" in exc_info.value.detail
        mock_logger.error.assert_called_once()


class TestDeleteCollection:
    """Tests for delete_collection endpoint"""

    @patch("ocr_backend.routers.collections.template_table")
    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_delete_collection_success(self, mock_logger, mock_vector_store, mock_template_table, admin_context):
        """Test successful collection deletion"""
        mock_vector_store.collection_exists.return_value = True
        mock_template_table.delete_templates_by_group_id.return_value = [
            "template1",
            "template2",
        ]
        mock_vector_store.delete_collection.return_value = True

        result = await delete_collection("test_collection", admin_context)

        assert result.success is True
        assert "deleted successfully" in result.message
        mock_template_table.delete_templates_by_group_id.assert_called_once_with("test_collection")
        mock_vector_store.delete_collection.assert_called_once_with("test_collection")

    @patch("ocr_backend.routers.collections.template_table")
    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_delete_collection_no_templates(
        self, mock_logger, mock_vector_store, mock_template_table, admin_context
    ):
        """Test collection deletion with no associated templates"""
        mock_vector_store.collection_exists.return_value = True
        mock_template_table.delete_templates_by_group_id.return_value = []
        mock_vector_store.delete_collection.return_value = True

        result = await delete_collection("test_collection", admin_context)

        assert result.success is True
        mock_logger.info.assert_called()

    @patch("ocr_backend.routers.collections.vector_store")
    async def test_delete_collection_not_found(self, mock_vector_store, admin_context):
        """Test deleting non-existent collection"""
        mock_vector_store.collection_exists.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await delete_collection("nonexistent", admin_context)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in exc_info.value.detail

    @patch("ocr_backend.routers.collections.template_table")
    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_delete_collection_template_error_continues(
        self, mock_logger, mock_vector_store, mock_template_table, admin_context
    ):
        """Test collection deletion continues even if template deletion fails"""
        mock_vector_store.collection_exists.return_value = True
        mock_template_table.delete_templates_by_group_id.side_effect = Exception("Template error")
        mock_vector_store.delete_collection.return_value = True

        result = await delete_collection("test_collection", admin_context)

        assert result.success is True
        mock_logger.warning.assert_called_once()
        mock_vector_store.delete_collection.assert_called_once()

    @patch("ocr_backend.routers.collections.template_table")
    @patch("ocr_backend.routers.collections.vector_store")
    async def test_delete_collection_deletion_fails(self, mock_vector_store, mock_template_table, admin_context):
        """Test when collection deletion fails"""
        mock_vector_store.collection_exists.return_value = True
        mock_template_table.delete_templates_by_group_id.return_value = []
        mock_vector_store.delete_collection.return_value = False

        with pytest.raises(HTTPException) as exc_info:
            await delete_collection("test_collection", admin_context)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to delete collection" in exc_info.value.detail

    @patch("ocr_backend.routers.collections.vector_store")
    @patch("ocr_backend.routers.collections.logger")
    async def test_delete_collection_exception(self, mock_logger, mock_vector_store, admin_context):
        """Test deleting collection with exception"""
        mock_vector_store.collection_exists.side_effect = Exception("Database error")

        with pytest.raises(HTTPException) as exc_info:
            await delete_collection("test_collection", admin_context)

        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Internal server error" in exc_info.value.detail
        mock_logger.error.assert_called_once()


class TestSchemas:
    """Tests for Pydantic schema models"""

    def test_collection_create_request_valid(self):
        """Test valid CollectionCreateRequest"""
        data = {
            "name": "test_collection",
            "vector_size": 128,
            "distance": DistanceMetric.COSINE,
        }
        request = CollectionCreateRequest(**data)
        assert request.name == "test_collection"
        assert request.vector_size == 128
        assert request.distance == DistanceMetric.COSINE
        assert request.on_disk_payload is True  # default
        assert request.replication_factor == 1  # default

    def test_collection_create_request_invalid_name(self):
        """Test CollectionCreateRequest with invalid name"""
        with pytest.raises(ValueError):
            CollectionCreateRequest(name="", vector_size=128)

    def test_collection_create_request_invalid_vector_size(self):
        """Test CollectionCreateRequest with invalid vector size"""
        with pytest.raises(ValueError):
            CollectionCreateRequest(name="test", vector_size=0)

    def test_collection_response_valid(self):
        """Test valid CollectionResponse"""
        response = CollectionResponse(
            name="test",
            vector_size=128,
            distance_metric="Cosine",
            points_count=100,
            status="green",
        )
        assert response.name == "test"
        assert response.vector_size == 128

    def test_collection_stats_response_valid(self):
        """Test valid CollectionStatsResponse"""
        response = CollectionStatsResponse(
            name="test",
            points_count=100,
            vector_size=128,
            distance_metric="Cosine",
            status="green",
        )
        assert response.name == "test"
        assert response.points_count == 100

    def test_collection_stats_response_with_error(self):
        """Test CollectionStatsResponse with error"""
        response = CollectionStatsResponse(
            name="test",
            points_count=0,
            error="Collection not found",
        )
        assert response.name == "test"
        assert response.error == "Collection not found"

    def test_message_response_valid(self):
        """Test valid MessageResponse"""
        response = MessageResponse(
            message="Operation successful",
            success=True,
        )
        assert response.message == "Operation successful"
        assert response.success is True
