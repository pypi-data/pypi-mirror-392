"""
Tests for the main Client class
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src import Client, BeforeSendResult
from src import ClientResponseError
from src import BaseAuthStore
from src import SendOptions


class TestClient:
    """Test cases for Client class."""
    
    def test_init_default(self):
        """Test client initialization with default values."""
        client = Client()
        
        assert client.base_url == ""
        assert client.lang == "en-US"
        assert isinstance(client.auth_store, BaseAuthStore)
        assert client.collections is not None
        assert client.health is not None
        assert client.logs is not None
        assert client.realtime is not None
    
    def test_init_custom(self):
        """Test client initialization with custom values."""
        auth_store = BaseAuthStore()
        client = Client(
            base_url="https://example.com",
            auth_store=auth_store,
            lang="fr-FR"
        )
        
        assert client.base_url == "https://example.com"
        assert client.lang == "fr-FR"
        assert client.auth_store is auth_store
    
    def test_base_url_property(self):
        """Test base_url property getter and setter."""
        client = Client()
        
        # Test getter
        client._base_url = "https://example.com/"
        assert client.base_url == "https://example.com"
        
        # Test setter
        client.base_url = "https://test.com/"
        assert client.base_url == "https://test.com"
        client.base_url = "https://test.com/api"
        assert client.base_url == "https://test.com/api"
    
    def test_admins_deprecated(self):
        """Test deprecated admins property."""
        client = Client()
        
        # Should return RecordService for _superusers collection
        admins_service = client.admins
        assert admins_service.collection_id_or_name == "_superusers"
    
    def test_create_batch(self):
        """Test batch service creation."""
        client = Client()
        
        batch = client.create_batch()
        assert batch is not None
        assert hasattr(batch, 'send')
        assert hasattr(batch, 'collection')
    
    def test_collection_service_caching(self):
        """Test collection service caching."""
        client = Client()
        
        # First call creates new service
        service1 = client.collection("users")
        assert service1.collection_id_or_name == "users"
        
        # Second call returns cached service
        service2 = client.collection("users")
        assert service1 is service2
        
        # Different collection creates new service
        service3 = client.collection("posts")
        assert service3.collection_id_or_name == "posts"
        assert service3 is not service1
    
    def test_auto_cancellation(self):
        """Test auto cancellation setting."""
        client = Client()
        
        # Default should be enabled
        assert client._enable_auto_cancellation is True
        
        # Test disabling
        returned_client = client.auto_cancellation(False)
        assert client._enable_auto_cancellation is False
        assert returned_client is client
        
        # Test enabling
        returned_client = client.auto_cancellation(True)
        assert client._enable_auto_cancellation is True
        assert returned_client is client
    
    def test_cancel_request(self):
        """Test request cancellation."""
        client = Client()
        
        # Mock controller
        mock_controller = MagicMock()
        mock_controller.cancel = MagicMock()
        client._cancel_controllers["test_key"] = mock_controller
        
        # Cancel request
        returned_client = client.cancel_request("test_key")
        
        assert "test_key" not in client._cancel_controllers
        mock_controller.cancel.assert_called_once()
        assert returned_client is client
    
    def test_cancel_all_requests(self):
        """Test cancelling all requests."""
        client = Client()
        
        # Mock controllers
        mock_controller1 = MagicMock()
        mock_controller1.cancel = MagicMock()
        mock_controller2 = MagicMock()
        mock_controller2.cancel = MagicMock()
        
        client._cancel_controllers["key1"] = mock_controller1
        client._cancel_controllers["key2"] = mock_controller2
        
        # Cancel all
        returned_client = client.cancel_all_requests()
        
        assert len(client._cancel_controllers) == 0
        mock_controller1.cancel.assert_called_once()
        mock_controller2.cancel.assert_called_once()
        assert returned_client is client
    
    def test_filter(self):
        """Test filter expression construction."""
        client = Client()
        
        # No parameters
        result = client.filter("title = 'test'")
        assert result == "title = 'test'"
        
        # With parameters
        result = client.filter(
            "title ~ {:title} && created >= {:created}",
            {"title": "test", "created": "2023-01-01"}
        )
        assert "title ~ 'test'" in result
        assert "created >= '2023-01-01'" in result
        
        # With different value types
        result = client.filter(
            "active = {:active} && count = {:count}",
            {"active": True, "count": 42}
        )
        assert "active = true" in result
        assert "count = 42" in result
    
    def test_build_url(self):
        """Test URL building."""
        client = Client()
        client._base_url = "https://example.com"
        
        # Basic path
        url = client.build_url("/api/collections")
        assert url == "https://example.com/api/collections"
        
        # Path with leading slash
        url = client.build_url("api/collections")
        assert url == "https://example.com/api/collections"
        
        # Empty path
        url = client.build_url("")
        assert url == "https://example.com"
        
        # Base URL with trailing slash
        client._base_url = "https://example.com/"
        url = client.build_url("/api/collections")
        assert url == "https://example.com/api/collections"
    
    def test_process_filter_value(self):
        """Test filter value processing."""
        client = Client()
        
        # None
        result = client._process_filter_value(None)
        assert result == "null"
        
        # Boolean
        result = client._process_filter_value(True)
        assert result == "true"
        result = client._process_filter_value(False)
        assert result == "false"
        
        # Number
        result = client._process_filter_value(42)
        assert result == "42"
        result = client._process_filter_value(3.14)
        assert result == "3.14"
        
        # String
        result = client._process_filter_value("test'string")
        assert result == "'test\\'string'"
        
        # Object
        result = client._process_filter_value({"key": "value"})
        assert result.startswith("'")
        assert result.endswith("'")
        assert "key" in result and "value" in result
    
    @pytest.mark.asyncio
    async def test_send_success(self):
        """Test successful request sending."""
        client = Client()
        
        mock_response_data = {"id": "test", "name": "Test"}
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_request.return_value.__aenter__.return_value = mock_response
            
            result = await client.send(
                "/api/test",
                SendOptions(method="GET")
            )
            
            assert result == mock_response_data
    
    @pytest.mark.asyncio
    async def test_send_error(self):
        """Test request error handling."""
        client = Client()
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.json = AsyncMock(return_value={"message": "Bad request"})
            mock_response.url = "https://example.com/api/test"
            mock_request.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ClientResponseError) as exc_info:
                await client.send(
                    "/api/test",
                    SendOptions(method="POST", body={"test": "data"})
                )
            
            assert exc_info.value.status == 400
            assert "Bad request" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_before_send_hook(self):
        """Test beforeSend hook."""
        client = Client()
        
        # Test dict return (legacy format)
        client.before_send = lambda url, options: {"headers": {"X-Test": "value"}}
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={})
            mock_request.return_value.__aenter__.return_value = mock_response
            
            await client.send("/api/test", SendOptions(method="GET"))
            
            # Check that headers were modified
            call_args = mock_request.call_args
            headers = call_args[1]['headers']
            assert "X-Test" in headers
        
        # Test BeforeSendResult return
        client.before_send = lambda url, options: BeforeSendResult(
            url="/api/modified",
            options=SendOptions(method="POST", headers={"X-Custom": "test"})
        )
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={})
            mock_request.return_value.__aenter__.return_value = mock_response
            
            await client.send("/api/test", SendOptions(method="GET"))
            
            # Check that URL and method were modified
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"  # method
            assert "/api/modified" in call_args[0][1]  # url
            headers = call_args[1]['headers']
            assert "X-Custom" in headers
    
    @pytest.mark.asyncio
    async def test_after_send_hook(self):
        """Test afterSend hook."""
        client = Client()
        
        # Modify response data in hook
        client.after_send = lambda response, data, options: {
            **data,
            "modified": True
        }
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"id": "test"})
            mock_request.return_value.__aenter__.return_value = mock_response
            
            result = await client.send("/api/test", SendOptions(method="GET"))
            
            assert result["id"] == "test"
            assert result["modified"] is True
    
    @pytest.mark.asyncio
    async def test_auth_headers(self):
        """Test that auth headers are added automatically."""
        client = Client()
        client.auth_store.save("test-token", None)
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={})
            mock_request.return_value.__aenter__.return_value = mock_response
            
            await client.send("/api/test", SendOptions(method="GET"))
            
            # Check that Authorization header was added
            call_args = mock_request.call_args
            headers = call_args[1]['headers']
            assert "Authorization" in headers
            assert headers["Authorization"] == "test-token"
    
    @pytest.mark.asyncio
    async def test_request_cancellation(self):
        """Test request cancellation functionality."""
        client = Client()
        client.auto_cancellation(True)
        
        options = SendOptions(method="GET", request_key="test-request")
        
        # First request should cancel previous one
        with patch('aiohttp.ClientSession.request') as mock_request:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={})
            mock_request.return_value.__aenter__.return_value = mock_response
            
            await client.send("/api/test", options)
            
            # Controller should be added and then canceled
            assert "test-request" in client._cancel_controllers
