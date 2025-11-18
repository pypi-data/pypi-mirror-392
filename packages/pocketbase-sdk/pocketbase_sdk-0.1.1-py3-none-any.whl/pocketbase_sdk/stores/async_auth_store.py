"""
Async authentication store for asynchronous environments
"""
import asyncio
from typing import Callable, Any
from .base_auth_store import BaseAuthStore, AuthRecord


class AsyncAuthStore(BaseAuthStore):
    """
    AuthStore that supports async operations and callbacks.
    
    This store extends BaseAuthStore with async capabilities,
    useful for asynchronous environments like asyncio applications.
    """
    
    def __init__(self):
        super().__init__()
        self._async_on_change_callbacks = []
    
    async def save_async(self, token: str, record: AuthRecord = None) -> None:
        """
        Asynchronously save token and record data.
        
        Args:
            token: Authentication token
            record: Auth record data
        """
        self.save(token, record)
        await self._trigger_async_change()
    
    async def clear_async(self) -> None:
        """Asynchronously clear auth data."""
        self.clear()
        await self._trigger_async_change()
    
    def on_async_change(self, callback: Callable[[str, AuthRecord], Any], fire_immediately: bool = False) -> Callable[[], None]:
        """
        Register an async callback function that will be called on store change.
        
        Args:
            callback: Async callback function to call on changes
            fire_immediately: Whether to call callback immediately
            
        Returns:
            Removal function that you could call to "unsubscribe" from the changes.
        """
        self._async_on_change_callbacks.append(callback)
        
        if fire_immediately:
            # Schedule the callback to run asynchronously
            asyncio.create_task(callback(self._base_token, self._base_model))
        
        def remove_callback():
            """Remove the callback from the list."""
            try:
                self._async_on_change_callbacks.remove(callback)
            except ValueError:
                pass  # Callback not found
        
        return remove_callback
    
    def on_change(self, callback: Callable[[str, AuthRecord], None], fire_immediately: bool = False) -> Callable[[], None]:
        """
        Register a synchronous callback function.
        
        This overrides the base method to ensure both sync and async callbacks are triggered.
        
        Args:
            callback: Synchronous callback function
            fire_immediately: Whether to call callback immediately
            
        Returns:
            Removal function
        """
        return super().on_change(callback, fire_immediately)
    
    def _trigger_change(self) -> None:
        """
        Override to trigger both sync and async callbacks.
        
        Note: Async callbacks are scheduled but not awaited here
        to avoid changing the synchronous nature of the parent method.
        """
        # Trigger sync callbacks
        super()._trigger_change()
        
        # Schedule async callbacks
        for callback in self._async_on_change_callbacks:
            try:
                asyncio.create_task(callback(self._base_token, self._base_model))
            except Exception:
                # If no event loop, ignore async callbacks
                pass
    
    async def _trigger_async_change(self) -> None:
        """Trigger all async change callbacks."""
        for callback in self._async_on_change_callbacks:
            try:
                await callback(self._base_token, self._base_model)
            except Exception:
                # Ignore callback errors to prevent breaking auth store
                pass
    
    async def get_valid_token_async(self) -> str:
        """
        Asynchronously get a valid token.
        
        Returns:
            Valid token or empty string
        """
        if self.is_valid:
            return self._base_token
        return ""
    
    async def refresh_if_needed_async(self, refresh_func: Callable[[], Any]) -> bool:
        """
        Asynchronously refresh token if needed.
        
        Args:
            refresh_func: Async function to call for refresh
            
        Returns:
            True if refresh was attempted, False otherwise
        """
        if not self.is_valid and self._base_token:
            try:
                await refresh_func()
                return True
            except Exception:
                return False
        return False
    
    def get_valid_token_sync(self) -> str:
        """
        Synchronously get a valid token.
        
        Returns:
            Valid token or empty string
        """
        return self._base_token if self.is_valid else ""
