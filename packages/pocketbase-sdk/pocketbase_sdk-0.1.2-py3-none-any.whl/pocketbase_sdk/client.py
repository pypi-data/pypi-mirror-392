"""
Main PocketBase client
"""
import json
import asyncio
from typing import Any, Callable, Dict, Optional, Union

from .utils.exceptions import ClientResponseError
from .stores import BaseAuthStore
from .stores.local_auth_store import LocalAuthStore
from .services.collection_service import CollectionService
from .services.health_service import HealthService
from .services import LogService
from .services import RecordService
from .services.batch_service import BatchService
from .services.realtime_service import RealtimeService
from .utils import SendOptions, normalize_unknown_query_params, serialize_query_params


class BeforeSendResult:
    """
    Result object for beforeSend hook modifications.
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        options: Optional[SendOptions] = None,
        **kwargs
    ):
        self.url = url
        self.options = options
        # Allow additional backward-compatible fields
        self.extra = kwargs


class Client:
    """
    PocketBase Python Client.
    
    This is the main client class for interacting with PocketBase API.
    It provides access to all services and manages authentication.
    """
    
    def __init__(
        self,
        base_url: str = "/",
        auth_store: Optional[BaseAuthStore] = None,
        lang: str = "en-US"
    ):
        """
        Initialize PocketBase client.
        
        Args:
            base_url: Base URL of PocketBase server
            auth_store: Custom auth store instance
            lang: Language code for requests
        """
        self.base_url = base_url.rstrip('/')
        self.lang = lang
        
        # Initialize auth store
        if auth_store:
            self.auth_store = auth_store
        else:
            self.auth_store = LocalAuthStore()
        
        # Internal state
        self._cancel_controllers: Dict[str, Any] = {}
        self._record_services: Dict[str, RecordService] = {}
        self._enable_auto_cancellation: bool = True
        
        # Service instances (lazy initialization to avoid circular dependency)
        self._collections_service: Optional[CollectionService] = None
        self._health_service: Optional[HealthService] = None
        self._logs_service: Optional[LogService] = None
        self._realtime_service: Optional[RealtimeService] = None
        
        # Hooks
        self.before_send: Optional[Callable[[str, SendOptions], Union[BeforeSendResult, Dict[str, Any]]]] = None
        self.after_send: Optional[Callable[[Any, Any, SendOptions], Any]] = None
    
    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._base_url
    
    @base_url.setter
    def base_url(self, value: str) -> None:
        """Set base URL."""
        self._base_url = value.rstrip('/')
    
    @property
    def collections(self) -> CollectionService:
        """Get collections service (lazy initialization)."""
        if self._collections_service is None:
            self._collections_service = CollectionService(self)
        return self._collections_service
    
    @property
    def health(self) -> HealthService:
        """Get health service (lazy initialization)."""
        if self._health_service is None:
            self._health_service = HealthService(self)
        return self._health_service
    
    @property
    def logs(self) -> LogService:
        """Get logs service (lazy initialization)."""
        if self._logs_service is None:
            self._logs_service = LogService(self)
        return self._logs_service
    
    @property
    def realtime(self) -> RealtimeService:
        """Get realtime service (lazy initialization)."""
        if self._realtime_service is None:
            self._realtime_service = RealtimeService(self)
        return self._realtime_service
    
    @property
    def admins(self) -> RecordService:
        """
        @deprecated
        With PocketBase v0.23.0 admins are converted to a regular auth
        collection named "_superusers", aka. you can use directly collection("_superusers").
        """
        return self.collection("_superusers")
    
    def create_batch(self) -> BatchService:
        """
        Create a new batch handler for sending multiple transactional requests.
        
        Returns:
            New BatchService instance
        """
        return BatchService(self)
    
    def collection(self, collection_id_or_name: str) -> RecordService:
        """
        Returns the RecordService associated to the specified collection.
        
        Args:
            collection_id_or_name: Collection ID or name
            
        Returns:
            RecordService for the collection
        """
        if collection_id_or_name not in self._record_services:
            self._record_services[collection_id_or_name] = RecordService(
                self,
                collection_id_or_name
            )
        
        return self._record_services[collection_id_or_name]
    
    def auto_cancellation(self, enable: bool) -> 'Client':
        """
        Globally enable or disable auto cancellation for pending duplicated requests.
        
        Args:
            enable: Whether to enable auto cancellation
            
        Returns:
            Self for chaining
        """
        self._enable_auto_cancellation = bool(enable)
        return self
    
    def cancel_request(self, request_key: str) -> 'Client':
        """
        Cancel single request by its cancellation key.
        
        Args:
            request_key: Request cancellation key
            
        Returns:
            Self for chaining
        """
        if request_key in self._cancel_controllers:
            controller = self._cancel_controllers[request_key]
            # Cancel the request (implementation depends on HTTP client)
            if hasattr(controller, 'cancel'):
                controller.cancel()
            del self._cancel_controllers[request_key]
        
        return self
    
    def cancel_all_requests(self) -> 'Client':
        """
        Cancel all pending requests.
        
        Returns:
            Self for chaining
        """
        for key in list(self._cancel_controllers.keys()):
            self.cancel_request(key)
        
        return self
    
    def filter(self, raw: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Construct a filter expression with placeholders populated from parameters.
        
        Placeholder parameters are defined with the `{:paramName}` notation.
        
        Args:
            raw: Raw filter expression
            params: Parameters to substitute
            
        Returns:
            Processed filter expression
        """
        if not params:
            return raw
        
        for key, value in params.items():
            processed_value = self._process_filter_value(value)
            raw = raw.replace(f"{{:{key}}}", processed_value)
        
        return raw
    
    def build_url(self, path: str) -> str:
        """
        Build a full client URL by safely concatenating the provided path.
        
        Args:
            path: Path to append to base URL
            
        Returns:
            Complete URL
        """
        url = self.base_url
        
        # Construct absolute base URL if relative
        if not url.startswith(('http://', 'https://')):
            # For relative URLs, we'll just use as-is
            # In a browser context, we'd construct absolute URLs
            pass
        
        # Concatenate the path
        if path:
            separator = "/" if not url.endswith("/") else ""
            path = path.lstrip("/")
            url = f"{url}{separator}{path}"
        
        return url
    
    async def send(self, path: str, options: SendOptions) -> Any:
        """
        Send an API HTTP request.
        
        Args:
            path: API path
            options: Request options
            
        Returns:
            Response data
            
        Raises:
            ClientResponseError: If request fails
        """
        options = self._init_send_options(path, options)
        
        # Build URL + path
        url = self.build_url(path)
        
        # Apply beforeSend hook
        if self.before_send:
            result = await self._call_before_send(url, options)
            if isinstance(result, BeforeSendResult):
                if result.url is not None:
                    url = result.url
                if result.options is not None:
                    options = result.options
            elif isinstance(result, dict):
                # Legacy format - merge with options
                for key, value in result.items():
                    if hasattr(options, key):
                        setattr(options, key, value)
                    else:
                        options.query[key] = value
        
        # Serialize query parameters
        if options.query:
            query_str = serialize_query_params(options.query)
            if query_str:
                separator = "&" if "?" in url else "?"
                url = f"{url}{separator}{query_str}"
            options.query = {}  # Clear query after serializing
        
        # Prepare request body
        body = self._prepare_body(options.body)
        
        # Prepare headers
        headers = self._prepare_headers(options.headers)
        
        # Send request using aiohttp
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=options.method,
                    url=url,
                    headers=headers,
                    json=body if headers.get('Content-Type') == 'application/json' else None,
                    data=body if headers.get('Content-Type') != 'application/json' else None,
                    timeout=30
                ) as response:
                    # Parse response
                    try:
                        response_data = await response.json()
                    except:
                        # All API responses are expected to return JSON
                        # with the exception of realtime events and 204
                        response_data = {}
                    
                    # Apply afterSend hook
                    if self.after_send:
                        response_data = await self._call_after_send(
                            response,
                            response_data,
                            options
                        )
                    
                    # Handle errors
                    if response.status >= 400:
                        raise ClientResponseError({
                            'url': str(response.url),
                            'status': response.status,
                            'data': response_data
                        })
                    
                    return response_data
        
        except aiohttp.ClientError as e:
            raise ClientResponseError(str(e))
        except Exception as e:
            raise ClientResponseError(str(e))
    
    def _init_send_options(self, path: str, options: SendOptions) -> SendOptions:
        """
        Initialize and normalize send options.
        
        Args:
            path: Request path
            options: Original options
            
        Returns:
            Normalized options
        """
        # Set defaults
        if not options.method:
            options.method = "GET"
        
        # Normalize unknown query params
        normalize_unknown_query_params(options)
        
        # Add default headers
        headers = options.headers or {}
        
        # Add Content-Type for JSON requests (not for FormData)
        if not headers.get('Content-Type') and options.body and options.method in ['POST', 'PUT', 'PATCH']:
            headers['Content-Type'] = 'application/json'
        
        # Add Accept-Language header
        if not headers.get('Accept-Language'):
            headers['Accept-Language'] = self.lang
        
        # Add Authorization header if token is available
        if self.auth_store.token and not headers.get('Authorization'):
            headers['Authorization'] = self.auth_store.token
        
        options.headers = headers
        
        # Handle request cancellation
        if self._enable_auto_cancellation and options.request_key is not None:
            request_key = options.request_key or f"{options.method}_{path}"
            
            # Cancel previous request with same key
            self.cancel_request(request_key)
            
            # Store controller for this request
            # Note: In real implementation, this would be an abort controller
            self._cancel_controllers[request_key] = None
        
        return options
    
    def _prepare_body(self, body: Any) -> Any:
        """
        Prepare request body for sending.
        
        Args:
            body: Raw body data
            
        Returns:
            Prepared body
        """
        if body is None:
            return None
        
        # If body is a dict and we're sending JSON, return as-is
        if isinstance(body, dict):
            return body
        
        # If body is a file-like object, return as-is
        if hasattr(body, 'read'):
            return body
        
        # For other types, convert to string
        return str(body)
    
    def _prepare_headers(self, headers: Optional[Dict[str, str]]) -> Dict[str, str]:
        """
        Prepare request headers.
        
        Args:
            headers: Raw headers
            
        Returns:
            Prepared headers
        """
        if not headers:
            return {}
        
        return {
            str(key): str(value)
            for key, value in headers.items()
        }
    
    async def _call_before_send(
        self,
        url: str,
        options: SendOptions
    ) -> Union[BeforeSendResult, Dict[str, Any]]:
        """
        Call beforeSend hook if available.
        
        Args:
            url: Request URL
            options: Request options
            
        Returns:
            Hook result
        """
        if not self.before_send:
            return {}
        
        if asyncio.iscoroutinefunction(self.before_send):
            return await self.before_send(url, options)
        else:
            return self.before_send(url, options)
    
    async def _call_after_send(
        self,
        response: Any,
        data: Any,
        options: SendOptions
    ) -> Any:
        """
        Call afterSend hook if available.
        
        Args:
            response: HTTP response
            data: Response data
            options: Request options
            
        Returns:
            Processed response data
        """
        if not self.after_send:
            return data
        
        if asyncio.iscoroutinefunction(self.after_send):
            return await self.after_send(response, data, options)
        else:
            return self.after_send(response, data, options)
    
    def _process_filter_value(self, value: Any) -> str:
        """
        Process a value for use in filter expressions.
        
        Args:
            value: Value to process
            
        Returns:
            String representation for filter
        """
        if value is None:
            return "null"
        
        if isinstance(value, bool):
            return "true" if value else "false"
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if isinstance(value, str):
            other = value.replace("'", "\\'")
            return f"'{other}'"
            # Escape single quotes
            # return f"'{value.replace(\"'\", \"\\'\")}'"
        
        if hasattr(value, 'isoformat'):  # datetime
            other = value.isoformat().replace('T', ' ')
            return f"'{other}'"
        
        # For other objects, JSON encode and escape
        json_str = json.dumps(value)
        replace = json_str.replace("'", "\\'")
        return f"'{replace}'"
        # return f"'{json_str.replace(\"'\", \"\\'\")}'"