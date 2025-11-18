"""
Request and response options
"""
from typing import Any, Dict, Optional
from dataclasses import dataclass
import json


@dataclass
class SendOptions:
    """Base options for sending requests."""
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    body: Any = None
    query: Optional[Dict[str, Any]] = None
    request_key: Optional[str] = None
    fetch_func: Optional[callable] = None
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {}
        if self.query is None:
            self.query = {}


@dataclass
class CommonOptions(SendOptions):
    """Common options with fields selection."""
    fields: Optional[str] = None


@dataclass
class ListOptions(CommonOptions):
    """Options for list requests."""
    page: Optional[int] = None
    per_page: Optional[int] = None
    sort: Optional[str] = None
    filter: Optional[str] = None
    skip_total: Optional[bool] = None


@dataclass
class FullListOptions(ListOptions):
    """Options for full list requests."""
    batch: Optional[int] = None


@dataclass
class RecordOptions(CommonOptions):
    """Options for record requests."""
    expand: Optional[str] = None


@dataclass
class RecordListOptions(ListOptions, RecordOptions):
    """Combined options for record list requests."""
    pass


@dataclass
class RecordFullListOptions(FullListOptions, RecordOptions):
    """Combined options for record full list requests."""
    pass


@dataclass
class RecordSubscribeOptions(SendOptions):
    """Options for record subscription."""
    fields: Optional[str] = None
    filter: Optional[str] = None
    expand: Optional[str] = None


@dataclass
class LogStatsOptions(CommonOptions):
    """Options for log statistics."""
    filter: Optional[str] = None


@dataclass
class FileOptions(CommonOptions):
    """Options for file operations."""
    thumb: Optional[str] = None
    download: Optional[bool] = None


@dataclass
class AuthOptions(CommonOptions):
    """Options for authentication requests."""
    auto_refresh_threshold: Optional[int] = None


# Known SendOptions keys (everything else is treated as query param)
KNOWN_SEND_OPTIONS_KEYS = {
    "method", "headers", "body", "query", "request_key", "fetch_func"
}


def normalize_unknown_query_params(options: Optional[SendOptions]) -> None:
    """
    Modify options in place by moving unknown send options as query parameters.
    
    Args:
        options: SendOptions object to normalize
    """
    if not options:
        return
    
    if options.query is None:
        options.query = {}
    
    # Get all instance variables that are not in known options
    known_keys = set(KNOWN_SEND_OPTIONS_KEYS)
    instance_vars = vars(options)
    
    for key, value in list(instance_vars.items()):
        if key not in known_keys and value is not None:
            options.query[key] = value
            delattr(options, key)


def serialize_query_params(params: Dict[str, Any]) -> str:
    """
    Serialize query parameters to a URL-encoded string.
    
    Args:
        params: Dictionary of query parameters
        
    Returns:
        URL-encoded query string
    """
    result = []
    
    for key, value in params.items():
        if value is None:
            continue
            
        encoded_key = str(key)
        
        # Handle array values
        if isinstance(value, list):
            for v in value:
                encoded_value = _prepare_query_param_value(v)
                if encoded_value is not None:
                    result.append(f"{encoded_key}={encoded_value}")
        else:
            encoded_value = _prepare_query_param_value(value)
            if encoded_value is not None:
                result.append(f"{encoded_key}={encoded_value}")
    
    return "&".join(result)


def _prepare_query_param_value(value: Any) -> Optional[str]:
    """
    Encode and normalize a query parameter value.
    
    Args:
        value: Value to encode
        
    Returns:
        Encoded string value or None if value should be skipped
    """
    if value is None:
        return None
    
    if isinstance(value, bool):
        return "true" if value else "false"
    
    if isinstance(value, (int, float)):
        return str(value)
    
    if isinstance(value, str):
        from urllib.parse import quote
        return quote(value)
    
    # Handle datetime objects
    if hasattr(value, 'isoformat'):
        # For datetime objects
        from urllib.parse import quote
        iso_str = value.isoformat().replace('T', ' ')
        return quote(iso_str)
    
    # Handle other objects
    if isinstance(value, dict) or isinstance(value, list):
        from urllib.parse import quote
        return quote(json.dumps(value))
    
    # Default: convert to string and encode
    from urllib.parse import quote
    return quote(str(value))
