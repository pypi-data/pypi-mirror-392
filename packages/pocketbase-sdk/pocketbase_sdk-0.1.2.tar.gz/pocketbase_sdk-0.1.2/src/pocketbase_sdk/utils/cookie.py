"""
Cookie utilities for PocketBase
"""

from typing import Dict, Any, Optional
from urllib.parse import quote, unquote
from datetime import datetime, timezone


def cookie_parse(cookie_string: str) -> Dict[str, str]:
    """
    Parse a cookie string into a dictionary.
    
    Args:
        cookie_string: Raw cookie header string
        
    Returns:
        Dictionary mapping cookie names to values
    """
    cookies = {}
    
    if not cookie_string:
        return cookies
    
    # Split on semicolons and process each cookie
    for cookie in cookie_string.split(';'):
        # Strip whitespace
        cookie = cookie.strip()
        
        if not cookie:
            continue
        
        # Find the first equals sign
        if '=' not in cookie:
            continue
        
        name, value = cookie.split('=', 1)
        
        # Decode URL-encoded parts
        try:
            name = unquote(name.strip())
            value = unquote(value.strip())
        except Exception:
            # If decoding fails, use as-is
            name = name.strip()
            value = value.strip()
        
        cookies[name] = value
    
    return cookies


def cookie_serialize(name: str, value: str, options: Optional[Dict[str, Any]] = None) -> str:
    """
    Serialize a cookie as a string.
    
    Args:
        name: Cookie name
        value: Cookie value
        options: Dictionary of cookie options
        
    Returns:
        Serialized cookie string
    """
    if not options:
        options = {}
    
    cookie_parts = []
    
    # Name and value
    cookie_parts.append(f"{name}={value}")
    
    # Expires
    if 'expires' in options:
        expires = options['expires']
        if isinstance(expires, datetime):
            # Format as GMT string
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            expires_str = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
            cookie_parts.append(f"Expires={expires_str}")
    
    # Max-Age
    if 'max_age' in options:
        max_age = options['max_age']
        if isinstance(max_age, int):
            cookie_parts.append(f"Max-Age={max_age}")
    
    # Domain
    if 'domain' in options:
        domain = options['domain']
        if domain:
            cookie_parts.append(f"Domain={domain}")
    
    # Path
    if 'path' in options:
        path = options['path']
        if path:
            cookie_parts.append(f"Path={path}")
    
    # Secure
    if options.get('secure', False):
        cookie_parts.append("Secure")
    
    # HttpOnly
    if options.get('httponly', False):
        cookie_parts.append("HttpOnly")
    
    # SameSite
    samesite = options.get('samesite')
    if samesite:
        if isinstance(samesite, bool):
            # True means Strict
            cookie_parts.append("SameSite=Strict")
        else:
            cookie_parts.append(f"SameSite={samesite}")
    
    return '; '.join(cookie_parts)


def is_cookie_size_valid(cookie_string: str) -> bool:
    """
    Check if cookie size is within the recommended 4096 bytes limit.
    
    Args:
        cookie_string: Serialized cookie string
        
    Returns:
        True if size is valid, False otherwise
    """
    return len(cookie_string.encode('utf-8')) <= 4096


def normalize_cookie_options(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize cookie options, handling various naming conventions.
    
    Args:
        options: Raw cookie options
        
    Returns:
        Normalized options dictionary
    """
    normalized = {}
    
    # Handle different naming conventions
    for key, value in options.items():
        if key.lower() in ['maxage', 'max-age']:
            normalized['max_age'] = value
        elif key.lower() in ['httponly', 'http_only']:
            normalized['httponly'] = value
        elif key.lower() in ['samesite', 'same_site']:
            normalized['samesite'] = value
        else:
            normalized[key.lower()] = value
    
    return normalized
