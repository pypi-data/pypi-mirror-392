"""
Health service for checking PocketBase server status
"""
from typing import Any, Dict, Optional
from .base_service import BaseService
from ..utils.options import CommonOptions


class HealthService(BaseService):
    """
    Service for checking PocketBase server health and status.
    
    This service provides methods to check if the server is running,
    get health metrics, and monitor system status.
    """
    
    async def check(self, options: Optional[CommonOptions] = None) -> Dict[str, Any]:
        """
        Perform a health check on the PocketBase server.
        
        Args:
            options: Additional request options
            
        Returns:
            Health check data
            
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
        
        return await self.client.send("/api/health", request_options)
    
    async def get_status(self, options: Optional[CommonOptions] = None) -> Dict[str, Any]:
        """
        Get detailed server status information.
        
        Args:
            options: Additional request options
            
        Returns:
            Server status data
            
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
        
        return await self.client.send("/api/health", request_options)
    
    async def is_healthy(self, options: Optional[CommonOptions] = None) -> bool:
        """
        Check if the server is healthy.
        
        Args:
            options: Additional request options
            
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            health_data = await self.check(options)
            return health_data.get("code", 0) == 200
        except Exception:
            return False
    
    async def get_database_stats(self, options: Optional[CommonOptions] = None) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Args:
            options: Additional request options
            
        Returns:
            Database statistics
            
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
        
        return await self.client.send("/api/health/database", request_options)
    
    async def get_cache_stats(self, options: Optional[CommonOptions] = None) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Args:
            options: Additional request options
            
        Returns:
            Cache statistics
            
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
        
        return await self.client.send("/api/health/cache", request_options)
    
    async def wait_until_healthy(
        self,
        timeout: int = 30,
        interval: int = 1,
        options: Optional[CommonOptions] = None
    ) -> bool:
        """
        Wait until the server becomes healthy.
        
        Args:
            timeout: Maximum time to wait in seconds
            interval: Check interval in seconds
            options: Additional request options
            
        Returns:
            True if server becomes healthy within timeout, False otherwise
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if await self.is_healthy(options):
                    return True
            except Exception:
                pass
            
            time.sleep(interval)
        
        return False
