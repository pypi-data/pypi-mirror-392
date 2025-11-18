"""
Tests for utility modules
"""
from datetime import datetime

from src import (
    RecordModel, ListResult, AuthMethodsList, RecordAuthResponse
)
from src import (
    SendOptions, ListOptions,
    normalize_unknown_query_params, serialize_query_params
)
from src import is_token_expired, get_token_payload
from src import cookie_parse, cookie_serialize


class TestDTOs:
    """Test cases for data transfer objects."""
    
    def test_base_model(self):
        """Test BaseModel functionality."""
        from src import BaseModel
        
        model = BaseModel(id="test-id")
        
        assert model.id == "test-id"
        
        # Dict-like access
        model["custom_field"] = "custom_value"
        assert model["custom_field"] == "custom_value"
        
        # Attribute access
        model.custom_attr = "custom"
        assert model.custom_attr == "custom"
    
    def test_record_model(self):
        """Test RecordModel."""
        record = RecordModel(
            id="test-id",
            collection_id="users",
            collection_name="users"
        )
        
        assert record.id == "test-id"
        assert record.collection_id == "users"
        assert record.collection_name == "users"
        
        # Dict-like access
        record["email"] = "test@example.com"
        assert record["email"] == "test@example.com"
    
    def test_list_result(self):
        """Test ListResult."""
        items = [{"id": "1"}, {"id": "2"}]
        
        result = ListResult(
            page=1,
            per_page=30,
            total_items=2,
            total_pages=1,
            items=items
        )
        
        assert result.page == 1
        assert result.per_page == 30
        assert result.total_items == 2
        assert result.total_pages == 1
        assert len(result.items) == 2
        assert result.items[0]["id"] == "1"
    
    def test_auth_methods_list(self):
        """Test AuthMethodsList."""
        data = {
            "mfa": {"enabled": True, "duration": 300},
            "otp": {"enabled": True, "duration": 300},
            "password": {"enabled": True, "identityFields": ["email"]},
            "oauth2": {"enabled": True, "providers": []}
        }
        
        auth_methods = AuthMethodsList(**data)
        
        assert auth_methods.mfa["enabled"] is True
        assert auth_methods.otp["duration"] == 300
        assert auth_methods.password["identityFields"] == ["email"]
        assert auth_methods.oauth2["enabled"] is True
    
    def test_record_auth_response(self):
        """Test RecordAuthResponse."""
        record = RecordModel(
            id="test-id",
            collection_id="users",
            collection_name="users"
        )
        
        auth_response = RecordAuthResponse(
            record=record,
            token="test-token",
            meta={"provider": "google"}
        )
        
        assert auth_response.record is record
        assert auth_response.token == "test-token"
        assert auth_response.meta["provider"] == "google"


class TestOptions:
    """Test cases for request options."""
    
    def test_send_options(self):
        """Test SendOptions."""
        options = SendOptions(
            method="POST",
            headers={"Content-Type": "application/json"},
            body={"test": "data"},
            query={"page": 1}
        )
        
        assert options.method == "POST"
        assert options.headers["Content-Type"] == "application/json"
        assert options.body["test"] == "data"
        assert options.query["page"] == 1
    
    def test_list_options(self):
        """Test ListOptions inheritance."""
        options = ListOptions(
            page=2,
            per_page=20,
            sort="created DESC",
            filter="status = 'active'",
            fields="id,name"
        )
        
        assert options.page == 2
        assert options.per_page == 20
        assert options.sort == "created DESC"
        assert options.filter == "status = 'active'"
        assert options.fields == "id,name"
    
    def test_normalize_unknown_query_params(self):
        """Test normalizing unknown query parameters."""
        options = SendOptions(
            method="GET",
            headers={},
            custom_param="custom_value",
            another_param="another_value"
        )
        
        normalize_unknown_query_params(options)
        
        assert options.query["custom_param"] == "custom_value"
        assert options.query["another_param"] == "another_value"
        assert not hasattr(options, "custom_param")
        assert not hasattr(options, "another_param")
    
    def test_serialize_query_params(self):
        """Test query parameter serialization."""
        params = {
            "page": 1,
            "per_page": 20,
            "filter": "name ~ 'test'",
            "fields": "id,name",
            "bool_param": True,
            "null_param": None,
            "list_param": ["value1", "value2"],
            "dict_param": {"key": "value"}
        }
        
        result = serialize_query_params(params)
        
        assert "page=1" in result
        assert "perPage=20" in result
        assert "filter=name%20~%20'test'" in result
        assert "fields=id%2Cname" in result
        assert "bool_param=true" in result
        assert "null_param" not in result
        assert "list_param=value1" in result
        assert "list_param=value2" in result
        assert "dict_param=%7B%22key%22%3A%22value%22%7D" in result  # URL encoded JSON
    
    def test_prepare_query_param_value(self):
        """Test query parameter value preparation."""
        from src import _prepare_query_param_value
        
        # None
        result = _prepare_query_param_value(None)
        assert result is None
        
        # Boolean
        result = _prepare_query_param_value(True)
        assert result == "true"
        result = _prepare_query_param_value(False)
        assert result == "false"
        
        # Number
        result = _prepare_query_param_value(42)
        assert result == "42"
        result = _prepare_query_param_value(3.14)
        assert result == "3.14"
        
        # String
        result = _prepare_query_param_value("test string")
        assert result == "test%20string"
        
        # Datetime
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = _prepare_query_param_value(dt)
        assert "2023-01-01%2012%3A00%3A00" in result
        
        # Dict
        result = _prepare_query_param_value({"key": "value"})
        assert result == "%7B%22key%22%3A%22value%22%7D"  # URL encoded JSON


class TestJWT:
    """Test cases for JWT utilities."""
    
    def test_is_token_expired_none(self):
        """Test expired check with None token."""
        assert is_token_expired(None) is True
        assert is_token_expired("") is True
    
    def test_is_token_expired_invalid(self):
        """Test expired check with invalid token."""
        assert is_token_expired("invalid.token.here") is True
        assert is_token_expired("not-a-token") is True
    
    def test_is_token_expired_valid_future(self):
        """Test expired check with future token."""
        import time
        from src import base64
        import json
        
        # Create token with future expiration
        future_time = int(time.time()) + 3600  # 1 hour from now
        payload = {"exp": future_time}
        payload_json = json.dumps(payload)
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
        
        token = f"header.{payload_b64}.signature"
        assert is_token_expired(token) is False
    
    def test_is_token_expired_past(self):
        """Test expired check with past token."""
        import time
        from src import base64
        import json
        
        # Create token with past expiration
        past_time = int(time.time()) - 3600  # 1 hour ago
        payload = {"exp": past_time}
        payload_json = json.dumps(payload)
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
        
        token = f"header.{payload_b64}.signature"
        assert is_token_expired(token) is True
    
    def test_get_token_payload_none(self):
        """Test payload extraction with None token."""
        payload = get_token_payload(None)
        assert payload == {}
        
        payload = get_token_payload("")
        assert payload == {}
    
    def test_get_token_payload_valid(self):
        """Test payload extraction with valid token."""
        from src import base64
        import json
        
        payload = {"id": "user-id", "type": "auth", "collectionId": "users"}
        payload_json = json.dumps(payload)
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
        
        token = f"header.{payload_b64}.signature"
        result = get_token_payload(token)
        
        assert result["id"] == "user-id"
        assert result["type"] == "auth"
        assert result["collectionId"] == "users"
    
    def test_get_token_payload_with_bearer(self):
        """Test payload extraction with Bearer token."""
        from src import base64
        import json
        
        payload = {"id": "user-id"}
        payload_json = json.dumps(payload)
        payload_b64 = base64.urlsafe_b64encode(payload_json.encode()).decode()
        
        token = f"Bearer header.{payload_b64}.signature"
        result = get_token_payload(token)
        
        assert result["id"] == "user-id"


class TestCookie:
    """Test cases for cookie utilities."""
    
    def test_cookie_parse(self):
        """Test cookie parsing."""
        cookie_string = "name1=value1; name2=value2; name3=value3 with spaces"
        
        cookies = cookie_parse(cookie_string)
        
        assert len(cookies) == 3
        assert cookies["name1"] == "value1"
        assert cookies["name2"] == "value2"
        assert cookies["name3"] == "value3 with spaces"
    
    def test_cookie_parse_empty(self):
        """Test parsing empty cookie string."""
        cookies = cookie_parse("")
        assert len(cookies) == 0
        
        cookies = cookie_parse("   ")
        assert len(cookies) == 0
    
    def test_cookie_parse_with_attributes(self):
        """Test parsing cookies with attributes."""
        cookie_string = "session=abc123; Path=/; HttpOnly; Secure; SameSite=Strict"
        
        cookies = cookie_parse(cookie_string)
        
        assert len(cookies) == 5
        assert cookies["session"] == "abc123"
        assert cookies["Path"] == "/"
        assert cookies["HttpOnly"] == ""
        assert cookies["Secure"] == ""
        assert cookies["SameSite"] == "Strict"
    
    def test_cookie_serialize(self):
        """Test cookie serialization."""
        options = {
            "expires": datetime(2023, 12, 31, 23, 59, 59),
            "max_age": 3600,
            "domain": "example.com",
            "path": "/",
            "secure": True,
            "httponly": True,
            "samesite": "Strict"
        }
        
        cookie = cookie_serialize("test", "value", options)
        
        assert cookie.startswith("test=value")
        assert "Expires=Sun, 31 Dec 2023 23:59:59 GMT" in cookie
        assert "Max-Age=3600" in cookie
        assert "Domain=example.com" in cookie
        assert "Path=/" in cookie
        assert "Secure" in cookie
        assert "HttpOnly" in cookie
        assert "SameSite=Strict" in cookie
    
    def test_cookie_serialize_minimal(self):
        """Test cookie serialization with minimal options."""
        cookie = cookie_serialize("name", "value")
        
        assert cookie == "name=value"
    
    def test_cookie_size_validation(self):
        """Test cookie size validation."""
        from src import is_cookie_size_valid
        
        # Small cookie
        small_cookie = "a=1"
        assert is_cookie_size_valid(small_cookie) is True
        
        # Large cookie (simulated)
        large_cookie = "x" * 5000
        assert is_cookie_size_valid(large_cookie) is False
    
    def test_normalize_cookie_options(self):
        """Test cookie options normalization."""
        from src import normalize_cookie_options
        
        options = {
            "MAXAGE": 3600,
            "HTTP_ONLY": True,
            "SAME_SITE": "Lax",
            "custom": "value"
        }
        
        normalized = normalize_cookie_options(options)
        
        assert normalized["max_age"] == 3600
        assert normalized["httponly"] is True
        assert normalized["samesite"] == "Lax"
        assert normalized["custom"] == "value"
