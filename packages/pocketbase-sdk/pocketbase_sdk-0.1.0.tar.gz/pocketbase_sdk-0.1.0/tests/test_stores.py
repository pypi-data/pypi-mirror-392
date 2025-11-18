"""
Tests for authentication stores
"""
import pytest
import tempfile
import os
from pathlib import Path

from src.stores.base_auth_store import BaseAuthStore
from src.stores.local_auth_store import LocalAuthStore
from src.stores.async_auth_store import AsyncAuthStore
from src.utils.dtos import RecordModel


class TestBaseAuthStore:
    """Test cases for BaseAuthStore."""
    
    def test_init(self):
        """Test store initialization."""
        store = BaseAuthStore()
        
        assert store.token == ""
        assert store.record is None
        assert store.model is None
        assert not store.is_valid
        assert not store.is_superuser
        assert len(store._on_change_callbacks) == 0
    
    def test_save_and_clear(self):
        """Test saving and clearing auth data."""
        store = BaseAuthStore()
        
        record = RecordModel(
            id="test-id",
            collection_id="users",
            collection_name="users"
        )
        
        # Save data
        store.save("test-token", record)
        
        assert store.token == "test-token"
        assert store.record is record
        assert store.model is record
        assert store.is_valid  # Assuming token is not expired
        
        # Clear data
        store.clear()
        
        assert store.token == ""
        assert store.record is None
        assert store.model is None
        assert not store.is_valid
    
    def test_on_change_callbacks(self):
        """Test change callback functionality."""
        store = BaseAuthStore()
        callback_calls = []
        
        def callback(token, record):
            callback_calls.append((token, record))
        
        # Add callback
        remove_callback = store.on_change(callback)
        
        # Save should trigger callback
        record = RecordModel(
            id="test-id",
            collection_id="users",
            collection_name="users"
        )
        store.save("test-token", record)
        
        assert len(callback_calls) == 1
        assert callback_calls[0] == ("test-token", record)
        
        # Clear should trigger callback
        store.clear()
        assert len(callback_calls) == 2
        assert callback_calls[1] == ("", None)
        
        # Remove callback
        remove_callback()
        store.save("new-token", None)
        assert len(callback_calls) == 2  # No new callback
    
    def test_on_change_fire_immediately(self):
        """Test fire_immediately option for on_change."""
        store = BaseAuthStore()
        callback_calls = []
        
        def callback(token, record):
            callback_calls.append((token, record))
        
        # Add callback with fire_immediately=True
        store.on_change(callback, fire_immediately=True)
        
        assert len(callback_calls) == 1
        assert callback_calls[0] == ("", None)
    
    def test_is_superuser(self):
        """Test superuser detection."""
        store = BaseAuthStore()
        
        # No token
        assert not store.is_superuser
        
        # User token (mocked)
        store.save("user-token", None)
        assert not store.is_superuser
        
        # Superuser record
        record = RecordModel(
            id="admin-id",
            collection_id="_superusers",
            collection_name="_superusers"
        )
        store.save("superuser-token", record)
        assert store.is_superuser
    
    def test_deprecated_properties(self):
        """Test deprecated properties with warnings."""
        store = BaseAuthStore()
        
        record = RecordModel(
            id="test-id",
            collection_id="users",
            collection_name="users"
        )
        store.save("test-token", record)
        
        # model property (deprecated)
        with pytest.warns(UserWarning):
            assert store.model is record
        
        # is_admin property (deprecated)
        with pytest.warns(UserWarning):
            assert not store.is_admin
        
        # is_auth_record property (deprecated)
        with pytest.warns(UserWarning):
            assert not store.is_auth_record
    
    def test_load_from_cookie(self):
        """Test loading auth data from cookie."""
        store = BaseAuthStore()
        
        # Valid cookie
        cookie_data = '{"token":"test-token","record":{"id":"test-id","collectionId":"users","collectionName":"users"}}'
        store.load_from_cookie(f"pb_auth={cookie_data}")
        
        assert store.token == "test-token"
        assert store.record is not None
        assert store.record.id == "test-id"
        
        # Invalid cookie
        store.clear()
        store.load_from_cookie("invalid_cookie")
        assert store.token == ""
        assert store.record is None
    
    def test_export_to_cookie(self):
        """Test exporting auth data to cookie."""
        store = BaseAuthStore()
        
        record = RecordModel(
            id="test-id",
            collection_id="users",
            collection_name="users"
        )
        store.save("test-token", record)
        
        cookie = store.export_to_cookie()
        
        assert "pb_auth=" in cookie
        assert "test-token" in cookie
        assert "test-id" in cookie


class TestLocalAuthStore:
    """Test cases for LocalAuthStore."""
    
    def test_init_default_path(self):
        """Test initialization with default path."""
        store = LocalAuthStore()
        
        assert store._storage_path.name == ".pocketbase_auth.json"
        assert store._key == "pb_auth"
    
    def test_init_custom_path(self):
        """Test initialization with custom path."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            store = LocalAuthStore(storage_path=temp_file.name, key="custom_key")
            
            assert store._storage_path == Path(temp_file.name)
            assert store._key == "custom_key"
            
            os.unlink(temp_file.name)
    
    def test_persistence(self):
        """Test that data persists across store instances."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Create first store and save data
            store1 = LocalAuthStore(storage_path=temp_file.name)
            record = RecordModel(
                id="test-id",
                collection_id="users",
                collection_name="users"
            )
            store1.save("test-token", record)
            
            # Create second store and verify data loaded
            store2 = LocalAuthStore(storage_path=temp_file.name)
            assert store2.token == "test-token"
            assert store2.record is not None
            assert store2.record.id == "test-id"
            
            # Clear and verify persistence
            store2.clear()
            store3 = LocalAuthStore(storage_path=temp_file.name)
            assert store3.token == ""
            assert store3.record is None
            
            os.unlink(temp_file.name)
    
    def test_export_import_file(self):
        """Test exporting and importing to/from file."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            with tempfile.NamedTemporaryFile(delete=False) as export_file:
                # Create store with data
                store = LocalAuthStore(storage_path=temp_file.name)
                record = RecordModel(
                    id="test-id",
                    collection_id="users",
                    collection_name="users"
                )
                store.save("test-token", record)
                
                # Export to file
                success = store.export_to_file(export_file.name)
                assert success
                
                # Clear store
                store.clear()
                
                # Import from file
                success = store.import_from_file(export_file.name)
                assert success
                assert store.token == "test-token"
                assert store.record is not None
                assert store.record.id == "test-id"
                
                os.unlink(temp_file.name)
                os.unlink(export_file.name)


@pytest.mark.asyncio
class TestAsyncAuthStore:
    """Test cases for AsyncAuthStore."""
    
    async def test_async_save_and_clear(self):
        """Test async save and clear operations."""
        store = AsyncAuthStore()
        
        record = RecordModel(
            id="test-id",
            collection_id="users",
            collection_name="users"
        )
        
        # Async save
        await store.save_async("test-token", record)
        
        assert store.token == "test-token"
        assert store.record is record
        
        # Async clear
        await store.clear_async()
        
        assert store.token == ""
        assert store.record is None
    
    async def test_async_callbacks(self):
        """Test async callback functionality."""
        store = AsyncAuthStore()
        sync_calls = []
        async_calls = []
        
        def sync_callback(token, record):
            sync_calls.append((token, record))
        
        async def async_callback(token, record):
            async_calls.append((token, record))
        
        # Add callbacks
        store.on_change(sync_callback)
        store.on_async_change(async_callback)
        
        # Save should trigger both callbacks
        record = RecordModel(
            id="test-id",
            collection_id="users",
            collection_name="users"
        )
        store.save("test-token", record)
        
        # Give async callbacks time to execute
        await asyncio.sleep(0.1)
        
        assert len(sync_calls) == 1
        assert len(async_calls) == 1
        assert sync_calls[0] == ("test-token", record)
        assert async_calls[0] == ("test-token", record)
    
    async def test_async_fire_immediately(self):
        """Test fire_immediately for async callbacks."""
        store = AsyncAuthStore()
        async_calls = []
        
        async def async_callback(token, record):
            async_calls.append((token, record))
        
        # Add callback with fire_immediately=True
        store.on_async_change(async_callback, fire_immediately=True)
        
        # Give async callback time to execute
        await asyncio.sleep(0.1)
        
        assert len(async_calls) == 1
        assert async_calls[0] == ("", None)
    
    async def test_get_valid_token_async(self):
        """Test async token validation."""
        store = AsyncAuthStore()
        
        # No token
        token = await store.get_valid_token_async()
        assert token == ""
        
        # Valid token (assuming not expired)
        from src.utils.jwt import is_token_expired
        test_token = "test.token.here"
        if not is_token_expired(test_token):
            store.save(test_token, None)
            token = await store.get_valid_token_async()
            assert token == test_token
        
        # Sync version
        token = store.get_valid_token_sync()
        assert token == test_token
