"""
Data Transfer Objects (DTOs) and type definitions
"""
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class BaseModel:
    """Base model with common fields."""
    id: str
    # Allow additional fields
    def __post_init__(self):
        # Store any additional fields passed that are not defined
        self._extra_fields: Dict[str, Any] = {}
        
    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access to additional fields"""
        if hasattr(self, key):
            return getattr(self, key)
        return self._extra_fields.get(key)
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Allow dict-like setting of additional fields"""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self._extra_fields[key] = value


@dataclass
class RecordModel(BaseModel):
    """Record model with collection information."""
    collection_id: str
    collection_name: str
    expand: Optional[Dict[str, Any]] = None


@dataclass
class ListResult:
    """Paginated list result."""
    page: int
    per_page: int
    total_items: int
    total_pages: int
    items: List[Any]


@dataclass
class LogModel(BaseModel):
    """Log entry model."""
    level: str
    message: str
    created: str
    updated: str
    data: Dict[str, Any]


# Collection field types
@dataclass
class CollectionField(BaseModel):
    """Collection field definition."""
    name: str
    type: str
    system: bool
    hidden: bool
    presentable: bool


@dataclass
class TokenConfig:
    """Token configuration."""
    duration: int
    secret: Optional[str] = None


@dataclass
class EmailTemplate:
    """Email template configuration."""
    subject: str
    body: str


@dataclass
class AuthAlertConfig:
    """Auth alert configuration."""
    enabled: bool
    email_template: EmailTemplate


@dataclass
class OTPConfig:
    """OTP configuration."""
    enabled: bool
    duration: int
    length: int
    email_template: EmailTemplate


@dataclass
class MFAConfig:
    """MFA configuration."""
    enabled: bool
    duration: int
    rule: str


@dataclass
class PasswordAuthConfig:
    """Password authentication configuration."""
    enabled: bool
    identity_fields: List[str]


@dataclass
class OAuth2Provider:
    """OAuth2 provider configuration."""
    name: str
    client_id: str
    client_secret: str
    auth_url: str
    token_url: str
    user_info_url: str
    display_name: str
    pkce: Optional[bool] = None
    extra: Optional[Dict[str, Any]] = None


@dataclass
class OAuth2Config:
    """OAuth2 configuration."""
    enabled: bool
    mapped_fields: Dict[str, str]
    providers: List[OAuth2Provider]


# Base collection types
@dataclass
class BaseCollectionModel(BaseModel):
    """Base collection model."""
    name: str
    fields: List[CollectionField]
    indexes: List[str]
    system: bool
    list_rule: Optional[str] = None
    view_rule: Optional[str] = None
    create_rule: Optional[str] = None
    update_rule: Optional[str] = None
    delete_rule: Optional[str] = None
    type: str = "base"


@dataclass
class ViewCollectionModel(BaseCollectionModel):
    """View collection model."""
    view_query: str =""
    type: str = "view"


@dataclass
class AuthCollectionModel(BaseCollectionModel):
    """Auth collection model."""
    auth_rule: Optional[str] = None
    manage_rule: Optional[str] = None
    auth_alert: Optional[AuthAlertConfig] = None
    oauth2: Optional[OAuth2Config] = None
    password_auth: Optional[PasswordAuthConfig] = None
    mfa: Optional[MFAConfig] = None
    otp: Optional[OTPConfig] = None
    
    auth_token: Optional[TokenConfig] = None
    password_reset_token: Optional[TokenConfig] = None
    email_change_token: Optional[TokenConfig] = None
    verification_token: Optional[TokenConfig] = None
    file_token: Optional[TokenConfig] = None
    
    verification_template: Optional[EmailTemplate] = None
    reset_password_template: Optional[EmailTemplate] = None
    confirm_email_change_template: Optional[EmailTemplate] = None
    type: str = "auth"


# Union type for all collection models
CollectionModel = Union[BaseCollectionModel, ViewCollectionModel, AuthCollectionModel]


@dataclass
class RecordAuthResponse:
    """Authentication response data."""
    record: RecordModel
    token: str
    meta: Optional[Dict[str, Any]] = None


@dataclass
class AuthProviderInfo:
    """OAuth2 provider information."""
    name: str
    display_name: str
    state: str
    auth_url: str
    code_verifier: str
    code_challenge: str
    code_challenge_method: str


@dataclass
class AuthMethodsList:
    """Available authentication methods."""
    mfa: Dict[str, Any]
    otp: Dict[str, Any]
    password: Dict[str, Any]
    oauth2: Dict[str, Any]


@dataclass
class RecordSubscription:
    """Realtime record subscription data."""
    action: str  # create, update, delete
    record: RecordModel


@dataclass
class OTPResponse:
    """OTP response data."""
    otp_id: str
