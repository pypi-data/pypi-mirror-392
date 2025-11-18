"""
PocketBase SDK exceptions
"""
from typing import Any, Dict, Optional


class ClientResponseError(Exception):
    """
    PocketBase client response error.
    
    This exception is raised when the API returns an error response.
    It contains details about the error response including status code,
    URL, and response data.
    """
    
    def __init__(self, error: Any):
        """
        Initialize the exception.
        
        Args:
            error: Can be a dict with error details or another Exception
        """
        super().__init__()
        
        if isinstance(error, dict):
            self.url = error.get("url", "")
            self.status = error.get("status", 0)
            self.data = error.get("data", {})
            self.is_api_error = True
        elif isinstance(error, Exception):
            self.url = ""
            self.status = 0
            self.data = {"message": str(error)}
            self.is_api_error = False
        else:
            self.url = ""
            self.status = 0
            self.data = {"message": str(error)}
            self.is_api_error = False
    
    @property
    def message(self) -> str:
        """Get the error message from the data."""
        if isinstance(self.data, dict):
            return self.data.get("message", "Unknown error")
        return str(self.data)
    
    def __str__(self) -> str:
        """String representation of the error."""
        if self.is_api_error:
            return f"ClientResponseError {self.status}: {self.message} ({self.url})"
        return f"ClientResponseError: {self.message}"
    
    def __repr__(self) -> str:
        """Detailed representation of the error."""
        return f"ClientResponseError(url='{self.url}', status={self.status}, data={self.data})"
