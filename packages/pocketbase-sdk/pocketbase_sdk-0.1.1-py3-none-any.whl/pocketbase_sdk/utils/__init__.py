"""
Utility modules for PocketBase Python SDK
"""
from .dtos import (
    BaseModel, RecordModel, ListResult, LogModel,
    CollectionField, TokenConfig, EmailTemplate, AuthAlertConfig,
    OTPConfig, MFAConfig, PasswordAuthConfig, OAuth2Provider,
    OAuth2Config, BaseCollectionModel, ViewCollectionModel,
    AuthCollectionModel, CollectionModel, RecordAuthResponse,
    AuthProviderInfo, AuthMethodsList, RecordSubscription, OTPResponse
)
from .options import (
    SendOptions, CommonOptions, ListOptions, FullListOptions,
    RecordOptions, RecordListOptions, RecordFullListOptions,
    RecordSubscribeOptions, LogStatsOptions, FileOptions, AuthOptions,
    normalize_unknown_query_params, serialize_query_params
)

__all__ = [
    # DTOs
    "BaseModel", "RecordModel", "ListResult", "LogModel",
    "CollectionField", "TokenConfig", "EmailTemplate", "AuthAlertConfig",
    "OTPConfig", "MFAConfig", "PasswordAuthConfig", "OAuth2Provider",
    "OAuth2Config", "BaseCollectionModel", "ViewCollectionModel",
    "AuthCollectionModel", "CollectionModel", "RecordAuthResponse",
    "AuthProviderInfo", "AuthMethodsList", "RecordSubscription", "OTPResponse",
    # Options
    "SendOptions", "CommonOptions", "ListOptions", "FullListOptions",
    "RecordOptions", "RecordListOptions", "RecordFullListOptions",
    "RecordSubscribeOptions", "LogStatsOptions", "FileOptions", "AuthOptions",
    "normalize_unknown_query_params", "serialize_query_params"
]
