"""
Base authentication store for PocketBase
"""
from typing import Callable, Optional, Any, Dict
from ..utils.dtos import RecordModel
from ..utils.jwt import is_token_expired, get_token_payload


AuthRecord = Optional[RecordModel]
AuthModel = AuthRecord  # backward compatibility
OnStoreChangeFunc = Callable[[str, AuthRecord], None]


class BaseAuthStore:
    """
    Base AuthStore class that stores the auth state in runtime memory 
    (aka. only for the duration of the store instance).
    
    Usually you wouldn't use it directly and instead use the builtin 
    LocalAuthStore, AsyncAuthStore or extend it with your own custom implementation.
    """
    
    def __init__(self):
        self._base_token: str = ""
        self._base_model: AuthRecord = None
        self._on_change_callbacks: list[OnStoreChangeFunc] = []
    
    @property
    def token(self) -> str:
        """Retrieves the stored token (if any)."""
        return self._base_token
    
    @property
    def record(self) -> AuthRecord:
        """Retrieves the stored model data (if any)."""
        return self._base_model
    
    @property
    def model(self) -> AuthRecord:
        """
        @deprecated use `record` instead.
        """
        return self._base_model
    
    @property
    def is_valid(self) -> bool:
        """
        Loosely checks if the store has valid token (aka. existing and unexpired exp claim).
        """
        return not is_token_expired(self._base_token)
    
    @property
    def is_superuser(self) -> bool:
        """
        Loosely checks whether the currently loaded store state is for superuser.
        
        Alternatively you can also compare directly `pb.auth_store.record.collection_name`.
        """
        payload = get_token_payload(self._base_token)
        
        return (
            payload.get("type") == "auth" and
            (
                (self._base_model and self._base_model.collection_name == "_superusers") or
                # fallback in case the record field is not populated and assuming
                # that the collection crc32 checksum id wasn't manually changed
                (not self._base_model or not hasattr(self._base_model, 'collection_name') and
                 payload.get("collectionId") == "pbc_3142635823")
            )
        )
    
    @property
    def is_admin(self) -> bool:
        """
        @deprecated use `is_superuser` instead or simply check the record.collection_name property.
        """
        print("Warning: Please replace pb.auth_store.is_admin with pb.auth_store.is_superuser OR simply check the value of pb.auth_store.record.collection_name")
        return self.is_superuser
    
    @property
    def is_auth_record(self) -> bool:
        """
        @deprecated use `!is_superuser` instead or simply check the record.collection_name property.
        """
        print("Warning: Please replace pb.auth_store.is_auth_record with !pb.auth_store.is_superuser OR simply check the value of pb.auth_store.record.collection_name")
        payload = get_token_payload(self._base_token)
        return payload.get("type") == "auth" and not self.is_superuser
    
    def save(self, token: str, record: AuthRecord = None) -> None:
        """
        Saves the provided new token and model data in the auth store.
        
        Args:
            token: Authentication token
            record: Auth record data
        """
        self._base_token = token or ""
        self._base_model = record or None
        
        self._trigger_change()
    
    def clear(self) -> None:
        """Removes the stored token and model data from the auth store."""
        self._base_token = ""
        self._base_model = None
        self._trigger_change()
    
    def load_from_cookie(self, cookie: str, key: str = "pb_auth") -> None:
        """
        Parses the provided cookie string and updates the store state
        with the cookie's token and model data.
        
        NB! This function doesn't validate the token or its data.
        Usually this isn't a concern if you are interacting only with the
        PocketBase API because it has the proper server-side security checks in place,
        but if you are using the store `is_valid` state for permission controls
        in a node server (eg. SSR), then it is recommended to call `auth_refresh()`
        after loading the cookie to ensure an up-to-date token and model state.
        
        Args:
            cookie: Cookie string to parse
            key: Cookie key to extract
        """
        try:
            import json
            from ..utils.cookie import cookie_parse
            
            cookies = cookie_parse(cookie or "")
            raw_data = cookies.get(key, "")
            
            data = {}
            try:
                data = json.loads(raw_data) if raw_data else {}
                # normalize
                if not isinstance(data, dict):
                    data = {}
            except (json.JSONDecodeError, ValueError):
                data = {}
            
            self.save(data.get("token", ""), data.get("record") or data.get("model"))
        except Exception:
            # If cookie parsing fails, clear the store
            self.clear()
    
    def export_to_cookie(self, options: Optional[Dict[str, Any]] = None, key: str = "pb_auth") -> str:
        """
        Exports the current store state as cookie string.
        
        By default the following optional attributes are added:
        - Secure
        - HttpOnly
        - SameSite=Strict
        - Path=/
        - Expires={the token expiration date}
        
        NB! If the generated cookie exceeds 4096 bytes, this method will
        strip the model data to the bare minimum to try to fit within the
        recommended size in https://www.rfc-editor.org/rfc/rfc6265#section-6.1.
        
        Args:
            options: Cookie serialization options
            key: Cookie key
            
        Returns:
            Serialized cookie string
        """
        from ..utils.cookie import cookie_serialize
        import json
        from datetime import datetime
        default_options = {
            "secure": True,
            "samesite": "Strict",
            "httponly": True,
            "path": "/",
        }
        
        # Extract the token expiration date
        payload = get_token_payload(self._base_token)
        if payload and "exp" in payload:

            default_options["expires"] = datetime.fromtimestamp(payload["exp"])
        else:
            default_options["expires"] = datetime(1970, 1, 1)
        
        # Merge with user defined options
        if options:
            default_options.update(options)
        
        raw_data = {
            "token": self._base_token,
            "record": json.loads(json.dumps(self._base_model.__dict__ if self._base_model else {}))
        }
        
        result = cookie_serialize(key, json.dumps(raw_data), default_options)
        
        # Check cookie size
        result_length = len(result)
        
        # Strip down the model data to the bare minimum
        if raw_data["record"] and result_length > 4096:
            minimal_record = {
                "id": raw_data["record"].get("id"),
                "email": raw_data["record"].get("email"),
            }
            extra_props = ["collectionId", "collectionName", "verified"]
            for prop in extra_props:
                if prop in raw_data["record"]:
                    minimal_record[prop] = raw_data["record"][prop]
            
            raw_data["record"] = minimal_record
            result = cookie_serialize(key, json.dumps(raw_data), default_options)
        
        return result
    
    def on_change(self, callback: OnStoreChangeFunc, fire_immediately: bool = False) -> Callable[[], None]:
        """
        Register a callback function that will be called on store change.
        
        You can set the `fire_immediately` argument to True in order to invoke
        the provided callback right after registration.
        
        Args:
            callback: Callback function to call on changes
            fire_immediately: Whether to call the callback immediately
            
        Returns:
            Removal function that you could call to "unsubscribe" from the changes.
        """
        self._on_change_callbacks.append(callback)
        
        if fire_immediately:
            callback(self._base_token, self._base_model)
        
        def remove_callback():
            """Remove the callback from the list."""
            try:
                self._on_change_callbacks.remove(callback)
            except ValueError:
                pass  # Callback not found
        
        return remove_callback
    
    def _trigger_change(self) -> None:
        """Trigger all registered change callbacks."""
        for callback in self._on_change_callbacks:
            try:
                callback(self._base_token, self._base_model)
            except Exception:
                # Ignore callback errors to prevent breaking the auth store
                pass
