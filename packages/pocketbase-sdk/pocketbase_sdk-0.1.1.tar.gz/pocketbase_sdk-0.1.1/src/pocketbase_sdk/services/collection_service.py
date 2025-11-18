"""
Collection service for managing database collections
"""
from typing import Any, Dict, List, Optional
from .crud_service import CrudService
from src.pocketbase_sdk.utils.dtos import CollectionModel, CollectionField
from src.pocketbase_sdk.utils.options import CommonOptions


class CollectionService(CrudService):
    """
    Service for managing database collections.
    
    This service provides CRUD operations for collections
    including creation, reading, updating, and deleting collections.
    """
    
    @property
    def base_crud_path(self) -> str:
        """Returns the base path for collection operations."""
        return "/api/collections"
    
    def decode(self, data: Dict[str, Any]) -> CollectionModel:
        """
        Decode collection response data into proper collection model.
        
        Args:
            data: Raw response data
            
        Returns:
            Properly typed collection model
        """
        collection_type = data.get('type', 'base')
        
        # Decode fields
        fields = []
        for field_data in data.get('fields', []):
            fields.append(CollectionField(
                id=field_data.get('id', ''),
                name=field_data.get('name', ''),
                type=field_data.get('type', ''),
                system=field_data.get('system', False),
                hidden=field_data.get('hidden', False),
                presentable=field_data.get('presentable', False)
            ))
        
        base_data = {
            'id': data.get('id', ''),
            'name': data.get('name', ''),
            'fields': fields,
            'indexes': data.get('indexes', []),
            'system': data.get('system', False),
            'list_rule': data.get('listRule'),
            'view_rule': data.get('viewRule'),
            'create_rule': data.get('createRule'),
            'update_rule': data.get('updateRule'),
            'delete_rule': data.get('deleteRule')
        }
        
        # Create appropriate collection type based on data
        if collection_type == 'auth':
            from ..utils.dtos import (
                AuthCollectionModel, AuthAlertConfig, OTPConfig, MFAConfig,
                PasswordAuthConfig, OAuth2Config, EmailTemplate, TokenConfig,
                OAuth2Provider
            )
            
            # Decode auth-specific fields
            auth_alert_data = data.get('authAlert', {})
            auth_alert = AuthAlertConfig(
                enabled=auth_alert_data.get('enabled', False),
                email_template=EmailTemplate(
                    subject=auth_alert_data.get('emailTemplate', {}).get('subject', ''),
                    body=auth_alert_data.get('emailTemplate', {}).get('body', '')
                )
            ) if auth_alert_data else None
            
            otp_data = data.get('otp', {})
            otp = OTPConfig(
                enabled=otp_data.get('enabled', False),
                duration=otp_data.get('duration', 0),
                length=otp_data.get('length', 0),
                email_template=EmailTemplate(
                    subject=otp_data.get('emailTemplate', {}).get('subject', ''),
                    body=otp_data.get('emailTemplate', {}).get('body', '')
                )
            ) if otp_data else None
            
            mfa_data = data.get('mfa', {})
            mfa = MFAConfig(
                enabled=mfa_data.get('enabled', False),
                duration=mfa_data.get('duration', 0),
                rule=mfa_data.get('rule', '')
            ) if mfa_data else None
            
            password_auth_data = data.get('passwordAuth', {})
            password_auth = PasswordAuthConfig(
                enabled=password_auth_data.get('enabled', False),
                identity_fields=password_auth_data.get('identityFields', [])
            ) if password_auth_data else None
            
            oauth2_data = data.get('oauth2', {})
            oauth2_providers = []
            for provider_data in oauth2_data.get('providers', []):
                oauth2_providers.append(OAuth2Provider(
                    name=provider_data.get('name', ''),
                    client_id=provider_data.get('clientId', ''),
                    client_secret=provider_data.get('clientSecret', ''),
                    auth_url=provider_data.get('authURL', ''),
                    token_url=provider_data.get('tokenURL', ''),
                    user_info_url=provider_data.get('userInfoURL', ''),
                    display_name=provider_data.get('displayName', ''),
                    pkce=provider_data.get('pkce'),
                    extra=provider_data.get('extra')
                ))
            
            oauth2 = OAuth2Config(
                enabled=oauth2_data.get('enabled', False),
                mapped_fields=oauth2_data.get('mappedFields', {}),
                providers=oauth2_providers
            ) if oauth2_data else None
            
            # Decode token configs
            def decode_token_config(token_data: Dict[str, Any]) -> TokenConfig:
                return TokenConfig(
                    duration=token_data.get('duration', 0),
                    secret=token_data.get('secret')
                )
            
            def decode_email_template(template_data: Dict[str, Any]) -> EmailTemplate:
                return EmailTemplate(
                    subject=template_data.get('subject', ''),
                    body=template_data.get('body', '')
                )
            
            return AuthCollectionModel(
                **base_data,
                auth_rule=data.get('authRule'),
                manage_rule=data.get('manageRule'),
                auth_alert=auth_alert,
                oauth2=oauth2,
                password_auth=password_auth,
                mfa=mfa,
                otp=otp,
                auth_token=decode_token_config(data.get('authToken', {})),
                password_reset_token=decode_token_config(data.get('passwordResetToken', {})),
                email_change_token=decode_token_config(data.get('emailChangeToken', {})),
                verification_token=decode_token_config(data.get('verificationToken', {})),
                file_token=decode_token_config(data.get('fileToken', {})),
                verification_template=decode_email_template(data.get('verificationTemplate', {})),
                reset_password_template=decode_email_template(data.get('resetPasswordTemplate', {})),
                confirm_email_change_template=decode_email_template(data.get('confirmEmailChangeTemplate', {}))
            )
            
        elif collection_type == 'view':
            from ..utils.dtos import ViewCollectionModel
            
            return ViewCollectionModel(
                **base_data,
                view_query=data.get('viewQuery', ''),
            )
            
        else:  # base
            from ..utils.dtos import BaseCollectionModel
            
            return BaseCollectionModel(**base_data)
    
    async def import_collections(
        self,
        collections: List[Dict[str, Any]],
        delete_missing: bool = False,
        options: Optional[CommonOptions] = None
    ) -> List[CollectionModel]:
        """
        Import collections in bulk.
        
        Args:
            collections: List of collection definitions
            delete_missing: Whether to delete collections not in the import
            options: Additional request options
            
        Returns:
            List of imported collections
            
        Raises:
            ClientResponseError: If import fails
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="PUT",
            body={
                "collections": collections,
                "deleteMissing": delete_missing
            },
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        response = await self.client.send(
            f"{self.base_crud_path}/import",
            request_options
        )
        
        return [self.decode(collection) for collection in response]
    
    async def get_schema(self, options: Optional[CommonOptions] = None) -> List[CollectionModel]:
        """
        Get the schema of all collections.
        
        Args:
            options: Additional request options
            
        Returns:
            List of collection schemas
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="GET",
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        response = await self.client.send(
            f"{self.base_crud_path}?skipTotal=1",
            request_options
        )
        
        return [self.decode(collection) for collection in response.get('items', [])]
    
    async def truncate(self, options: Optional[CommonOptions] = None) -> bool:
        """
        Truncate all records in all non-system collections.
        
        ⚠️ This action will delete all user data and cannot be undone!
        
        Args:
            options: Additional request options
            
        Returns:
            True if truncation was successful
            
        Raises:
            ClientResponseError: If truncation fails
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="DELETE",
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        await self.client.send(
            f"{self.base_crud_path}/truncate",
            request_options
        )
        
        return True
    
    async def backup(
        self,
        options: Optional[CommonOptions] = None
    ) -> Any:
        """
        Create a new database backup.
        
        Args:
            options: Additional request options
            
        Returns:
            Backup information
            
        Raises:
            ClientResponseError: If backup fails
        """
        if options is None:
            options = CommonOptions()
        
        request_options = CommonOptions(
            method="POST",
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        response = await self.client.send(
            f"{self.base_crud_path}/backup",
            request_options
        )
        
        return response
    
    async def get_one(self, id: str, options: Optional[CommonOptions] = None) -> CollectionModel:
        """Override to return proper CollectionModel type."""
        return await super().get_one(id, options)
    
    async def get_list(self, page: int = 1, per_page: int = 30, options=None) -> Any:
        """Override to return properly typed list."""
        return await super().get_list(page, per_page, options)
    
    async def get_full_list(self, batch: int = 200, options=None) -> List[CollectionModel]:
        """Override to return list of CollectionModel."""
        return await super().get_full_list(batch, options)
    
    async def create(self, body_params=None, options=None) -> CollectionModel:
        """Override to return proper CollectionModel type."""
        return await super().create(body_params, options)
    
    async def update(self, id: str, body_params=None, options=None) -> CollectionModel:
        """Override to return proper CollectionModel type."""
        return await super().update(id, body_params, options)
