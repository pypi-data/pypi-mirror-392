"""
Record service for collection operations
"""
from typing import Any, Dict, List, Optional, Union, Callable
from urllib.parse import quote

from .crud_service import CrudService
from .realtime_service import UnsubscribeFunc
from src.pocketbase_sdk.utils.dtos import (
    RecordModel, RecordAuthResponse, AuthMethodsList,
    RecordSubscription, OTPResponse
)
from src.pocketbase_sdk.utils.options import (
    RecordOptions, RecordListOptions, RecordFullListOptions,
    RecordSubscribeOptions, CommonOptions, AuthOptions
)
from src.pocketbase_sdk.utils.jwt import get_token_payload


class RecordService(CrudService):
    """
    Service for managing records in a specific collection.
    
    This service extends CrudService with additional authentication
    and real-time subscription capabilities.
    """
    
    def __init__(self, client, collection_id_or_name: str):
        """
        Initialize record service.
        
        Args:
            client: PocketBase client instance
            collection_id_or_name: Collection ID or name
        """
        super().__init__(client)
        self.collection_id_or_name = collection_id_or_name
    
    @property
    def base_crud_path(self) -> str:
        """Returns the base CRUD path for records."""
        return f"{self.base_collection_path}/records"
    
    @property
    def base_collection_path(self) -> str:
        """Returns the base collection path."""
        return f"/api/collections/{quote(self.collection_id_or_name)}"
    
    @property
    def is_superusers(self) -> bool:
        """Returns whether the current service collection is superusers."""
        return (
            self.collection_id_or_name == "_superusers" or
            self.collection_id_or_name == "_pbc_2773867675"
        )
    
    # ---------------------------------------------------------------
    # Realtime handlers
    # ---------------------------------------------------------------
    
    async def subscribe(
        self,
        topic: str,
        callback: Callable[[RecordSubscription], None],
        options: Optional[RecordSubscribeOptions] = None
    ) -> UnsubscribeFunc:
        """
        Subscribe to realtime changes to the specified topic.
        
        Args:
            topic: Topic name ("*" or record id)
            callback: Callback function for subscription events
            options: Subscription options
            
        Returns:
            Unsubscribe function
            
        Raises:
            ValueError: If topic or callback is missing
            ClientResponseError: If subscription fails
        """
        if not topic:
            raise ValueError("Missing topic.")
        
        if not callback:
            raise ValueError("Missing subscription callback.")
        
        return await self.client.realtime.subscribe(
            f"{self.collection_id_or_name}/{topic}",
            callback,
            options
        )
    
    async def unsubscribe(self, topic: Optional[str] = None) -> None:
        """
        Unsubscribe from realtime subscriptions.
        
        Args:
            topic: Topic to unsubscribe from (None for all)
        """
        if topic:
            # Unsubscribe from specific topic
            await self.client.realtime.unsubscribe(f"{self.collection_id_or_name}/{topic}")
        else:
            # Unsubscribe from everything related to the collection
            await self.client.realtime.unsubscribe_by_prefix(self.collection_id_or_name)
    
    # ---------------------------------------------------------------
    # CRUD overrides
    # ---------------------------------------------------------------
    
    async def get_full_list(
        self,
        batch_or_options: Union[int, RecordFullListOptions] = 200,
        options: Optional[RecordListOptions] = None
    ) -> List[RecordModel]:
        """
        Get full list with flexible parameter handling.
        
        Args:
            batch_or_options: Either batch size (int) or options
            options: Additional options if batch_or_options is int
            
        Returns:
            List of records
        """
        if isinstance(batch_or_options, int):
            # Legacy format: batch size + options
            full_options = RecordFullListOptions(batch=batch_or_options)
            if options:
                # Merge additional options
                for key, value in vars(options).items():
                    if value is not None and hasattr(full_options, key):
                        setattr(full_options, key, value)
            return await super().get_full_list(full_options.batch, full_options)
        else:
            # New format: options object
            return await super().get_full_list(batch_or_options.batch or 200, batch_or_options)
    
    async def get_list(
        self,
        page: int = 1,
        per_page: int = 30,
        options: Optional[RecordListOptions] = None
    ) -> Any:
        """Get paginated list of records."""
        return await super().get_list(page, per_page, options)
    
    async def get_first_list_item(
        self,
        filter_expr: str,
        options: Optional[RecordListOptions] = None
    ) -> RecordModel:
        """Get first item matching filter."""
        return await super().get_first_list_item(filter_expr, options)
    
    async def get_one(
        self,
        id: str,
        options: Optional[RecordOptions] = None
    ) -> RecordModel:
        """Get single record by ID."""
        return await super().get_one(id, options)
    
    async def create(
        self,
        body_params: Optional[Union[Dict[str, Any], Any]] = None,
        options: Optional[RecordOptions] = None
    ) -> RecordModel:
        """Create new record."""
        return await super().create(body_params, options)
    
    async def update(
        self,
        id: str,
        body_params: Optional[Union[Dict[str, Any], Any]] = None,
        options: Optional[RecordOptions] = None
    ) -> RecordModel:
        """
        Update record and handle auth store updates if needed.
        
        If the current client.auth_store.record matches with the updated id,
        then on success the client.auth_store.record will be updated.
        """
        item = await super().update(id, body_params, options)
        
        # Update auth store if this is the current authenticated record
        if (
            self.client.auth_store.record and
            self.client.auth_store.record.id == item.get('id') and
            (
                (hasattr(self.client.auth_store.record, 'collection_id') and 
                 self.client.auth_store.record.collection_id == self.collection_id_or_name) or
                (hasattr(self.client.auth_store.record, 'collection_name') and 
                 self.client.auth_store.record.collection_name == self.collection_id_or_name)
            )
        ):
            # Merge existing auth record with updated data
            auth_record = dict(self.client.auth_store.record.__dict__)
            if '_extra_fields' in auth_record:
                extra_fields = auth_record.pop('_extra_fields')
                auth_record.update(extra_fields)
            
            # Update with new data
            auth_record.update(item)
            
            # Preserve expand if it existed
            if self.client.auth_store.record.expand:
                auth_record['expand'] = self.client.auth_store.record.expand
            
            # Update auth store
            self.client.auth_store.save(self.client.auth_store.token, auth_record)
        
        return item
    
    async def delete(
        self,
        id: str,
        options: Optional[CommonOptions] = None
    ) -> bool:
        """
        Delete record and handle auth store updates if needed.
        
        If the current client.auth_store.record matches with the deleted id,
        then on success the client.auth_store will be cleared.
        """
        success = await super().delete(id, options)
        
        # Clear auth store if this is the current authenticated record
        if (
            success and
            self.client.auth_store.record and
            self.client.auth_store.record.id == id and
            (
                (hasattr(self.client.auth_store.record, 'collection_id') and 
                 self.client.auth_store.record.collection_id == self.collection_id_or_name) or
                (hasattr(self.client.auth_store.record, 'collection_name') and 
                 self.client.auth_store.record.collection_name == self.collection_id_or_name)
            )
        ):
            self.client.auth_store.clear()
        
        return success
    
    # ---------------------------------------------------------------
    # Auth handlers
    # ---------------------------------------------------------------
    
    def _auth_response(self, response_data: Dict[str, Any]) -> RecordAuthResponse:
        """
        Prepare successful collection authorization response.
        
        Args:
            response_data: Raw response from API
            
        Returns:
            Normalized auth response
        """
        record_data = response_data.get('record', {})
        record = self.decode(record_data)
        
        # Update auth store
        self.client.auth_store.save(
            response_data.get('token', ''),
            record
        )
        
        return RecordAuthResponse(
            record=record,
            token=response_data.get('token', ''),
            meta=response_data.get('meta')
        )
    
    async def list_auth_methods(
        self,
        options: Optional[CommonOptions] = None
    ) -> AuthMethodsList:
        """
        Returns all available collection auth methods.
        
        Args:
            options: Additional request options
            
        Returns:
            List of available auth methods
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="GET",
            query={"fields": "mfa,otp,password,oauth2"},
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Merge with existing query
        if options.query:
            request_options.query.update(options.query)
        
        response = await self.client.send(
            f"{self.base_collection_path}/auth-methods",
            request_options
        )
        
        return AuthMethodsList(**response)
    
    async def auth_with_password(
        self,
        username_or_email: str,
        password: str,
        options: Optional[AuthOptions] = None
    ) -> RecordAuthResponse:
        """
        Authenticate with username/email and password.
        
        Args:
            username_or_email: Username or email
            password: Password
            options: Additional auth options
            
        Returns:
            Authentication response
            
        Raises:
            ClientResponseError: If authentication fails
        """
        if options is None:
            options = AuthOptions()
        
        request_options = AuthOptions(
            method="POST",
            body={
                "identity": username_or_email,
                "password": password
            },
            query=options.query,
            headers=options.headers,
            request_key=options.request_key,
            auto_refresh_threshold=options.auto_refresh_threshold
        )
        
        response = await self.client.send(
            f"{self.base_collection_path}/auth-with-password",
            request_options
        )
        
        return self._auth_response(response)
    
    async def auth_with_oauth2_code(
        self,
        provider: str,
        code: str,
        code_verifier: str,
        redirect_url: str,
        create_data: Optional[Dict[str, Any]] = None,
        options: Optional[RecordOptions] = None
    ) -> RecordAuthResponse:
        """
        Authenticate with OAuth2 code.
        
        Args:
            provider: OAuth2 provider name
            code: Authorization code
            code_verifier: PKCE code verifier
            redirect_url: Redirect URL
            create_data: Optional record creation data
            options: Additional request options
            
        Returns:
            Authentication response
        """
        if options is None:
            options = RecordOptions()
        
        request_options = RecordOptions(
            method="POST",
            body={
                "provider": provider,
                "code": code,
                "codeVerifier": code_verifier,
                "redirectURL": redirect_url,
                "createData": create_data or {}
            },
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        response = await self.client.send(
            f"{self.base_collection_path}/auth-with-oauth2",
            request_options
        )
        
        return self._auth_response(response)
    
    async def auth_refresh(
        self,
        options: Optional[RecordOptions] = None
    ) -> RecordAuthResponse:
        """
        Refresh authentication token.
        
        Args:
            options: Additional request options
            
        Returns:
            Authentication response
        """
        if options is None:
            options = RecordOptions()
        
        request_options = RecordOptions(
            method="POST",
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        response = await self.client.send(
            f"{self.base_collection_path}/auth-refresh",
            request_options
        )
        
        return self._auth_response(response)
    
    async def request_password_reset(
        self,
        email: str,
        options: Optional[CommonOptions] = None
    ) -> bool:
        """
        Send password reset request.
        
        Args:
            email: Email address
            options: Additional request options
            
        Returns:
            True if request was sent successfully
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="POST",
            body={"email": email},
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        await self.client.send(
            f"{self.base_collection_path}/request-password-reset",
            request_options
        )
        
        return True
    
    async def confirm_password_reset(
        self,
        password_reset_token: str,
        password: str,
        password_confirm: str,
        options: Optional[CommonOptions] = None
    ) -> bool:
        """
        Confirm password reset with token.
        
        Args:
            password_reset_token: Password reset token
            password: New password
            password_confirm: Password confirmation
            options: Additional request options
            
        Returns:
            True if reset was successful
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="POST",
            body={
                "token": password_reset_token,
                "password": password,
                "passwordConfirm": password_confirm
            },
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        await self.client.send(
            f"{self.base_collection_path}/confirm-password-reset",
            request_options
        )
        
        return True
    
    async def request_verification(
        self,
        email: str,
        options: Optional[CommonOptions] = None
    ) -> bool:
        """
        Send email verification request.
        
        Args:
            email: Email address
            options: Additional request options
            
        Returns:
            True if request was sent successfully
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="POST",
            body={"email": email},
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        await self.client.send(
            f"{self.base_collection_path}/request-verification",
            request_options
        )
        
        return True
    
    async def confirm_verification(
        self,
        verification_token: str,
        options: Optional[CommonOptions] = None
    ) -> bool:
        """
        Confirm email verification.
        
        Args:
            verification_token: Verification token
            options: Additional request options
            
        Returns:
            True if verification was successful
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="POST",
            body={"token": verification_token},
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        await self.client.send(
            f"{self.base_collection_path}/confirm-verification",
            request_options
        )
        
        # Update current auth record if it matches the verified token
        payload = get_token_payload(verification_token)
        model = self.client.auth_store.record
        
        if (
            model and
            not model.verified and
            model.id == payload.get('id') and
            hasattr(model, 'collection_id') and
            model.collection_id == payload.get('collectionId')
        ):
            model.verified = True
            self.client.auth_store.save(self.client.auth_store.token, model)
        
        return True
    
    async def request_email_change(
        self,
        new_email: str,
        options: Optional[CommonOptions] = None
    ) -> bool:
        """
        Send email change request.
        
        Args:
            new_email: New email address
            options: Additional request options
            
        Returns:
            True if request was sent successfully
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="POST",
            body={"newEmail": new_email},
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        await self.client.send(
            f"{self.base_collection_path}/request-email-change",
            request_options
        )
        
        return True
    
    async def confirm_email_change(
        self,
        email_change_token: str,
        password: str,
        options: Optional[CommonOptions] = None
    ) -> bool:
        """
        Confirm email change.
        
        Args:
            email_change_token: Email change token
            password: Current password
            options: Additional request options
            
        Returns:
            True if email change was successful
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="POST",
            body={
                "token": email_change_token,
                "password": password
            },
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        await self.client.send(
            f"{self.base_collection_path}/confirm-email-change",
            request_options
        )
        
        # Clear auth store if this matches the current authenticated record
        payload = get_token_payload(email_change_token)
        model = self.client.auth_store.record
        
        if (
            model and
            model.id == payload.get('id') and
            hasattr(model, 'collection_id') and
            model.collection_id == payload.get('collectionId')
        ):
            self.client.auth_store.clear()
        
        return True
    
    async def request_otp(
        self,
        email: str,
        options: Optional[CommonOptions] = None
    ) -> OTPResponse:
        """
        Send OTP request.
        
        Args:
            email: Email address
            options: Additional request options
            
        Returns:
            OTP response with otp_id
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="POST",
            body={"email": email},
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        response = await self.client.send(
            f"{self.base_collection_path}/request-otp",
            request_options
        )
        
        return OTPResponse(**response)
    
    async def auth_with_otp(
        self,
        otp_id: str,
        password: str,
        options: Optional[CommonOptions] = None
    ) -> RecordAuthResponse:
        """
        Authenticate with OTP.
        
        Args:
            otp_id: OTP ID
            password: OTP password
            options: Additional request options
            
        Returns:
            Authentication response
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="POST",
            body={"otpId": otp_id, "password": password},
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        response = await self.client.send(
            f"{self.base_collection_path}/auth-with-otp",
            request_options
        )
        
        return self._auth_response(response)
    
    async def impersonate(
        self,
        record_id: str,
        duration: int,
        options: Optional[CommonOptions] = None
    ):
        """
        Impersonate a user by record ID.
        
        This action currently requires superusers privileges.
        
        Args:
            record_id: Record ID to impersonate
            duration: Token duration in seconds
            options: Additional request options
            
        Returns:
            New client instance with impersonated auth state
        """
        if options is None:
            options = CommonOptions()
        
        from ..stores.base_auth_store import BaseAuthStore
        from ..client import Client
        
        request_options = CommonOptions(
            method="POST",
            body={"duration": duration},
            query=options.query,
            headers={"Authorization": self.client.auth_store.token, **(options.headers or {})},
            request_key=options.request_key
        )
        
        # Create new client for impersonation
        impersonated_client = Client(
            self.client.base_url,
            BaseAuthStore(),
            self.client.lang
        )
        
        auth_data = await impersonated_client.send(
            f"{self.base_collection_path}/impersonate/{quote(record_id)}",
            request_options
        )
        
        impersonated_client.auth_store.save(
            auth_data.get('token', ''),
            self.decode(auth_data.get('record', {}))
        )
        
        return impersonated_client
