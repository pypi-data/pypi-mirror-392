"""
JWT utilities for PocketBase
"""
import base64
import json
from typing import Any, Dict, Optional


def is_token_expired(token: str) -> bool:
    """
    Checks if the JWT token has expired.
    
    Args:
        token: JWT token string
        
    Returns:
        True if token is expired or invalid, False otherwise
    """
    try:
        payload = get_token_payload(token)
        if not payload or "exp" not in payload:
            return True
        
        import time
        current_time = int(time.time())
        exp_time = int(payload["exp"])
        
        return current_time >= exp_time
    except Exception:
        return True


def get_token_payload(token: str) -> Dict[str, Any]:
    """
    Decodes the JWT payload without verification (for offline checks).
    
    Args:
        token: JWT token string
        
    Returns:
        Token payload as dictionary, empty dict if invalid
    """
    if not token:
        return {}
    
    try:
        # Remove Bearer prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Split token parts
        parts = token.split('.')
        if len(parts) != 3:
            return {}
        
        # Decode payload (second part)
        payload = parts[1]
        
        # Add padding if needed
        padding = len(payload) % 4
        if padding:
            payload += '=' * (4 - padding)
        
        # Base64 decode
        decoded_bytes = base64.urlsafe_b64decode(payload)
        decoded_str = decoded_bytes.decode('utf-8')
        
        return json.loads(decoded_str)
    except Exception:
        return {}


def decode_token(token: str) -> Dict[str, Any]:
    """
    Full JWT token decoding (header and payload).
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary with header and payload, empty dict if invalid
    """
    if not token:
        return {}
    
    try:
        # Remove Bearer prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        # Split token parts
        parts = token.split('.')
        if len(parts) != 3:
            return {}
        
        result = {}
        
        # Decode header
        header = parts[0]
        padding = len(header) % 4
        if padding:
            header += '=' * (4 - padding)
        
        decoded_bytes = base64.urlsafe_b64decode(header)
        result["header"] = json.loads(decoded_bytes.decode('utf-8'))
        
        # Decode payload
        payload = parts[1]
        padding = len(payload) % 4
        if padding:
            payload += '=' * (4 - padding)
        
        decoded_bytes = base64.urlsafe_b64decode(payload)
        result["payload"] = json.loads(decoded_bytes.decode('utf-8'))
        
        return result
    except Exception:
        return {}
