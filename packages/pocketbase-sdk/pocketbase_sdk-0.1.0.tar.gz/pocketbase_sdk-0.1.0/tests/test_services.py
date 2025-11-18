"""
Tests for API services
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.collection_service import CollectionService
from src.services.health_service import HealthService
from src.services.log_service import LogService
from src.services.record_service import RecordService
from src.services.batch_service import BatchService, BatchCollectionService
from src.client import Client
from src.utils.dtos import (
    CollectionModel, BaseCollectionModel, AuthCollectionModel,
    LogModel, ListResult, RecordAuthResponse
)
from src.utils.options import CommonOptions, ListOptions, SendOptions


@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    client = Client()
    client.send = AsyncMock()
    return client


class TestCollectionService:
    """Test cases for CollectionService."""
    
    def test_base_path(self):
        """Test base CRUD path."""
        client = Client()
        service = CollectionService(client)
        
        assert service.base_crud_path == "/api/collections"
    
    def test_decode_base_collection(self, mock_client):
        """Test decoding base collection."""
        service = CollectionService(mock_client)
        
        data = {
            "id": "test-id",
            "name": "test_collection",
            "type": "base",
            "system": False,
            "fields": [
                {
                    "id": "field-id",
                    "name": "title",
                    "type": "text",
                    "system": False,
                    "hidden": False,
                    "presentable": True
                }
            ],
            "indexes": ["idx_title"],
            "listRule": "true",
            "viewRule": "true",
            "createRule": "true",
            "updateRule": "true",
            "deleteRule": "true"
        }
        
        result = service.decode(data)
        
        assert isinstance(result, BaseCollectionModel)
        assert result.id == "test-id"
        assert result.name == "test_collection"
        assert result.type == "base"
        assert len(result.fields) == 1
        assert result.fields[0].name == "title"
        assert result.list_rule == "true"
    
    def test_decode_auth_collection(self, mock_client):
        """Test decoding auth collection."""
        service = CollectionService(mock_client)
        
        data = {
            "id": "test-id",
            "name": "users",
            "type": "auth",
            "system": False,
            "fields": [],
            "indexes": [],
            "authRule": "id = @request.auth.id",
            "manageRule": "true",
            "passwordAuth": {
                "enabled": True,
                "identityFields": ["email"]
            },
            "authToken": {
                "duration": 604800
            }
        }
        
        result = service.decode(data)
        
        assert isinstance(result, AuthCollectionModel)
        assert result.type == "auth"
        assert result.auth_rule == "id = @request.auth.id"
        assert result.manage_rule == "true"
        assert result.password_auth.enabled is True
        assert result.password_auth.identity_fields == ["email"]
        assert result.auth_token.duration == 604800
    
    @pytest.mark.asyncio
    async def test_get_schema(self, mock_client):
        """Test getting collection schema."""
        service = CollectionService(mock_client)
        
        mock_response = {
            "items": [
                {
                    "id": "test-id",
                    "name": "test_collection",
                    "type": "base",
                    "system": False,
                    "fields": [],
                    "indexes": []
                }
            ]
        }
        mock_client.send.return_value = mock_response
        
        result = await service.get_schema()
        
        assert len(result) == 1
        assert isinstance(result[0], BaseCollectionModel)
        assert result[0].name == "test_collection"
        
        # Verify correct API call
        mock_client.send.assert_called_once()
        call_args = mock_client.send.call_args
        assert "skipTotal=1" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_import_collections(self, mock_client):
        """Test importing collections."""
        service = CollectionService(mock_client)
        
        collections = [
            {
                "name": "test_collection",
                "type": "base",
                "fields": []
            }
        ]
        mock_response = [
            {
                "id": "imported-id",
                "name": "test_collection",
                "type": "base",
                "fields": []
            }
        ]
        mock_client.send.return_value = mock_response
        
        result = await service.import_collections(collections, delete_missing=False)
        
        assert len(result) == 1
        assert result[0].id == "imported-id"
        
        # Verify correct API call
        mock_client.send.assert_called_once()
        call_args = mock_client.send.call_args
        call_data = call_args[0][1].body
        assert call_data["collections"] == collections
        assert call_data["deleteMissing"] is False
    
    @pytest.mark.asyncio
    async def test_truncate(self, mock_client):
        """Test truncating all collections."""
        service = CollectionService(mock_client)
        
        mock_client.send.return_value = {}
        
        result = await service.truncate()
        
        assert result is True
        
        # Verify correct API call
        mock_client.send.assert_called_once()
        call_args = mock_client.send.call_args
        assert call_args[0][0] == "/api/collections/truncate"
        assert call_args[0][1].method == "DELETE"


class TestHealthService:
    """Test cases for HealthService."""
    
    @pytest.mark.asyncio
    async def test_check(self, mock_client):
        """Test health check."""
        service = HealthService(mock_client)
        
        mock_response = {"code": 200, "message": "OK"}
        mock_client.send.return_value = mock_response
        
        result = await service.check()
        
        assert result["code"] == 200
        assert result["message"] == "OK"
        
        mock_client.send.assert_called_once()
        call_args = mock_client.send.call_args
        assert call_args[0][0] == "/api/health"
    
    @pytest.mark.asyncio
    async def test_is_healthy(self, mock_client):
        """Test health status check."""
        service = HealthService(mock_client)
        
        # Healthy response
        mock_client.send.return_value = {"code": 200}
        result = await service.is_healthy()
        assert result is True
        
        # Unhealthy response
        mock_client.send.return_value = {"code": 500}
        result = await service.is_healthy()
        assert result is False
        
        # Exception handling
        mock_client.send.side_effect = Exception("Connection error")
        result = await service.is_healthy()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_wait_until_healthy(self, mock_client):
        """Test waiting for healthy status."""
        import time
        service = HealthService(mock_client)
        
        # Immediate healthy
        mock_client.send.return_value = {"code": 200}
        start_time = time.time()
        result = await service.wait_until_healthy(timeout=5)
        end_time = time.time()
        
        assert result is True
        assert end_time - start_time < 1
        
        # Immediate unhealthy (timeout)
        mock_client.send.side_effect = Exception("Connection error")
        start_time = time.time()
        result = await service.wait_until_healthy(timeout=1)
        end_time = time.time()
        
        assert result is False
        assert end_time - start_time >= 1


class TestLogService:
    """Test cases for LogService."""
    
    @pytest.mark.asyncio
    async def test_get_list(self, mock_client):
        """Test getting log list."""
        service = LogService(mock_client)
        
        mock_response = {
            "page": 1,
            "perPage": 30,
            "totalItems": 1,
            "totalPages": 1,
            "items": [
                {
                    "id": "log-id",
                    "level": "info",
                    "message": "Test message",
                    "created": "2023-01-01 12:00:00",
                    "updated": "2023-01-01 12:00:00",
                    "data": {}
                }
            ]
        }
        mock_client.send.return_value = mock_response
        
        result = await service.get_list()
        
        assert isinstance(result, ListResult)
        assert result.page == 1
        assert result.per_page == 30
        assert result.total_items == 1
        assert len(result.items) == 1
        
        log_item = result.items[0]
        assert isinstance(log_item, LogModel)
        assert log_item.id == "log-id"
        assert log_item.level == "info"
        assert log_item.message == "Test message"
    
    @pytest.mark.asyncio
    async def test_get_error_logs(self, mock_client):
        """Test getting error logs."""
        service = LogService(mock_client)
        
        mock_response = {
            "page": 1,
            "perPage": 30,
            "totalItems": 0,
            "totalPages": 1,
            "items": []
        }
        mock_client.send.return_value = mock_response
        
        result = await service.get_error_logs()
        
        # Should call get_list with error filter
        mock_client.send.assert_called()
        call_args = mock_client.send.call_args
        assert "level != 'debug'" in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_delete_logs_older_than(self, mock_client):
        """Test deleting old logs."""
        service = LogService(mock_client)
        
        mock_client.send.return_value = {}
        
        result = await service.delete_logs_older_than(30)
        
        assert result is True
        
        # Verify correct API call
        mock_client.send.assert_called_once()
        call_args = mock_client.send.call_args
        assert call_args[0][0] == "/api/logs/cleanup"
        assert call_args[0][1].method == "DELETE"
        assert call_args[0][1].body["days"] == 30


class TestRecordService:
    """Test cases for RecordService."""
    
    def test_init(self, mock_client):
        """Test record service initialization."""
        service = RecordService(mock_client, "users")
        
        assert service.collection_id_or_name == "users"
        assert not service.is_superusers
        
        # Superusers collection
        service_superuser = RecordService(mock_client, "_superusers")
        assert service_superuser.is_superusers
    
    def test_base_paths(self, mock_client):
        """Test base paths."""
        service = RecordService(mock_client, "users")
        
        assert service.base_collection_path == "/api/collections/users"
        assert service.base_crud_path == "/api/collections/users/records"
    
    @pytest.mark.asyncio
    async def test_auth_with_password(self, mock_client):
        """Test password authentication."""
        service = RecordService(mock_client, "users")
        
        mock_response = {
            "token": "test-token",
            "record": {
                "id": "user-id",
                "collectionId": "users",
                "collectionName": "users",
                "email": "test@example.com"
            }
        }
        mock_client.send.return_value = mock_response
        
        result = await service.auth_with_password("test@example.com", "password")
        
        assert isinstance(result, RecordAuthResponse)
        assert result.token == "test-token"
        assert result.record.id == "user-id"
        assert result.record.email == "test@example.com"
        
        # Verify auth store was updated
        assert mock_client.auth_store.token == "test-token"
        assert mock_client.auth_store.record is not None
        assert mock_client.auth_store.record.id == "user-id"
        
        # Verify correct API call
        mock_client.send.assert_called_once()
        call_args = mock_client.send.call_args
        assert call_args[0][0] == "/api/collections/users/auth-with-password"
        assert call_args[0][1].method == "POST"
        assert call_args[0][1].body["identity"] == "test@example.com"
        assert call_args[0][1].body["password"] == "password"
    
    @pytest.mark.asyncio
    async def test_subscribe_and_unsubscribe(self, mock_client):
        """Test subscription functionality."""
        service = RecordService(mock_client, "users")
        
        # Mock realtime service
        mock_realtime = MagicMock()
        mock_client.realtime = mock_realtime
        mock_realtime.subscribe = AsyncMock(return_value=lambda: None)
        mock_realtime.unsubscribe = AsyncMock()
        mock_realtime.unsubscribe_by_prefix = AsyncMock()
        
        callback = MagicMock()
        
        # Subscribe
        unsubscribe_func = await service.subscribe("test-topic", callback)
        
        mock_realtime.subscribe.assert_called_once_with(
            "users/test-topic",
            callback,
            None
        )
        assert callable(unsubscribe_func)
        
        # Unsubscribe specific topic
        await service.unsubscribe("test-topic")
        mock_realtime.unsubscribe.assert_called_with("users/test-topic")
        
        # Unsubscribe all
        await service.unsubscribe()
        mock_realtime.unsubscribe_by_prefix.assert_called_with("users")


class TestBatchService:
    """Test cases for BatchService."""
    
    def test_init(self, mock_client):
        """Test batch service initialization."""
        service = BatchService(mock_client)
        
        assert service.base_path == "/api/batch"
        assert service.count() == 0
    
    def test_collection_service(self, mock_client):
        """Test getting collection service."""
        batch_service = BatchService(mock_client)
        collection_service = batch_service.collection("users")
        
        assert isinstance(collection_service, BatchCollectionService)
        assert collection_service.collection_id_or_name == "users"
        assert collection_service.batch_service is batch_service
    
    @pytest.mark.asyncio
    async def test_batch_operations(self, mock_client):
        """Test adding batch operations."""
        batch_service = BatchService(mock_client)
        
        # Add operations
        collection_service = batch_service.collection("users")
        
        collection_service.create({"name": "User 1"})
        collection_service.update("user-1", {"name": "Updated User 1"})
        collection_service.delete("user-2")
        collection_service.upsert({"id": "user-3", "name": "User 3"})
        collection_service.patch("user-4", {"name": "Patched User 4"})
        
        assert batch_service.count() == 5
        
        # Mock send response
        mock_response = [
            {"id": "created-id", "name": "User 1"},
            {"id": "user-1", "name": "Updated User 1"},
            True,  # Delete success
            {"id": "user-3", "name": "User 3"},
            {"id": "user-4", "name": "Patched User 4"}
        ]
        mock_client.send.return_value = mock_response
        
        # Send batch
        result = await batch_service.send()
        
        assert len(result) == 5
        assert batch_service.count() == 0  # Should be cleared after send
        
        # Verify correct API call
        mock_client.send.assert_called_once()
        call_args = mock_client.send.call_args
        assert call_args[0][0] == "/api/batch"
        assert call_args[0][1].method == "POST"
        assert len(call_args[0][1].body["batch"]) == 5
    
    @pytest.mark.asyncio
    async def test_send_empty_batch(self, mock_client):
        """Test sending empty batch should raise error."""
        batch_service = BatchService(mock_client)
        
        with pytest.raises(ValueError, match="No batch items added"):
            await batch_service.send()
    
    def test_clear_batch(self, mock_client):
        """Test clearing batch items."""
        batch_service = BatchService(mock_client)
        
        collection_service = batch_service.collection("users")
        collection_service.create({"name": "Test"})
        
        assert batch_service.count() == 1
        
        batch_service.clear()
        assert batch_service.count() == 0


class TestBatchCollectionService:
    """Test cases for BatchCollectionService."""
    
    def test_create_operation(self, mock_client):
        """Test create operation."""
        batch_service = BatchService(mock_client)
        collection_service = batch_service.collection("users")
        
        result = collection_service.create({"name": "Test User"})
        
        assert result is batch_service
        assert batch_service.count() == 1
        
        batch_items = batch_service._batch_items
        assert batch_items[0]["collection"] == "users"
        assert batch_items[0]["action"] == "create"
        assert batch_items[0]["body"]["name"] == "Test User"
    
    def test_update_operation(self, mock_client):
        """Test update operation."""
        batch_service = BatchService(mock_client)
        collection_service = batch_service.collection("users")
        
        result = collection_service.update("user-id", {"name": "Updated Name"})
        
        assert result is batch_service
        assert batch_service.count() == 1
        
        batch_items = batch_service._batch_items
        assert batch_items[0]["collection"] == "users"
        assert batch_items[0]["action"] == "update"
        assert batch_items[0]["body"]["id"] == "user-id"
        assert batch_items[0]["body"]["name"] == "Updated Name"
    
    def test_delete_operation(self, mock_client):
        """Test delete operation."""
        batch_service = BatchService(mock_client)
        collection_service = batch_service.collection("users")
        
        result = collection_service.delete("user-id")
        
        assert result is batch_service
        assert batch_service.count() == 1
        
        batch_items = batch_service._batch_items
        assert batch_items[0]["collection"] == "users"
        assert batch_items[0]["action"] == "delete"
        assert batch_items[0]["body"]["id"] == "user-id"
    
    def test_upsert_operation(self, mock_client):
        """Test upsert operation."""
        batch_service = BatchService(mock_client)
        collection_service = batch_service.collection("users")
        
        result = collection_service.upsert({"id": "user-id", "name": "Upserted User"})
        
        assert result is batch_service
        assert batch_service.count() == 1
        
        batch_items = batch_service._batch_items
        assert batch_items[0]["collection"] == "users"
        assert batch_items[0]["action"] == "upsert"
        assert batch_items[0]["body"]["id"] == "user-id"
        assert batch_items[0]["body"]["name"] == "Upserted User"
