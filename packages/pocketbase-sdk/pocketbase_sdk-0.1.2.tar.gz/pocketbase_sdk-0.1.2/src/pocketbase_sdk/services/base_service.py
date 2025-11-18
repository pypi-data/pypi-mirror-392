"""
Base service class for PocketBase
"""
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client


class BaseService(ABC):
    """
    BaseService class that should be inherited from all API services.
    """
    
    def __init__(self, client: 'Client'):
        """
        Initialize service with client.
        
        Args:
            client: PocketBase client instance
        """
        self.client = client
