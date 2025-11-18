"""
PocketBase Python SDK
A Python client library for PocketBase backend.
"""

from .client import Client
from .exceptions import ClientResponseError
from .services.collection_service import CollectionService
from .services.health_service import HealthService
from .services.log_service import LogService
from .services.record_service import RecordService
from .services.crud_service import CrudService
from .services.batch_service import BatchService
from .stores.base_auth_store import BaseAuthStore
from .stores.local_auth_store import LocalAuthStore
from .stores.async_auth_store import AsyncAuthStore
from .utils.dtos import ListResult, RecordModel, CollectionModel
from .utils.options import CommonOptions, SendOptions

__version__ = "0.1.0"
__author__ = "PocketBase Python SDK"

# Export main classes
__all__ = [
    "Client",
    "ClientResponseError",
    "CollectionService",
    "HealthService", 
    "LogService",
    "RecordService",
    "CrudService",
    "BatchService",
    "BaseAuthStore",
    "LocalAuthStore", 
    "AsyncAuthStore",
    "ListResult",
    "RecordModel",
    "CollectionModel",
    "CommonOptions",
    "SendOptions",
]

# Default export
Client = Client
