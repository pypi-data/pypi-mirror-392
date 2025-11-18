"""
Log service for accessing PocketBase server logs
"""
from typing import Any, Dict, Optional
from .base_service import BaseService
from src.pocketbase_sdk.utils.dtos import LogModel, ListResult
from src.pocketbase_sdk.utils.options import LogStatsOptions


class LogService(BaseService):
    """
    Service for accessing PocketBase server logs.
    
    This service provides methods to retrieve and manage
    server logs including filtering and statistics.
    """
    
    async def get_list(
        self,
        page: int = 1,
        per_page: int = 30,
        options: Optional[LogStatsOptions] = None
    ) -> ListResult:
        """
        Fetches paginated list of log entries.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 30)
            options: Additional request options
            
        Returns:
            Paginated list of log entries
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = LogStatsOptions()
        
        # Build query parameters
        query = {
            'page': page,
            'perPage': per_page
        }
        
        # Add option-specific parameters
        if options.page is not None:
            query['page'] = options.page
        if options.per_page is not None:
            query['perPage'] = options.per_page
        if options.sort:
            query['sort'] = options.sort
        if options.filter:
            query['filter'] = options.filter
        if options.fields:
            query['fields'] = options.fields
        
        # Merge with existing query
        if options.query:
            query.update(options.query)
        
        # Prepare request options
        request_options = LogStatsOptions(
            method="GET",
            query=query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send request
        response = await self.client.send("/api/logs", request_options)
        
        # Convert to ListResult with LogModel items
        items = []
        for item in response.get('items', []):
            items.append(LogModel(
                id=item.get('id', ''),
                level=item.get('level', ''),
                message=item.get('message', ''),
                created=item.get('created', ''),
                updated=item.get('updated', ''),
                data=item.get('data', {})
            ))
        
        return ListResult(
            page=response.get('page', page),
            per_page=response.get('perPage', per_page),
            total_items=response.get('totalItems', 0),
            total_pages=response.get('totalPages', 0),
            items=items
        )
    
    async def get_one(self, id: str, options: Optional[LogStatsOptions] = None) -> LogModel:
        """
        Fetches a single log entry by its ID.
        
        Args:
            id: Log entry ID
            options: Additional request options
            
        Returns:
            Log entry
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = LogStatsOptions()
        
        # Build query parameters
        query = {}
        if options.fields:
            query['fields'] = options.fields
        
        # Merge with existing query
        if options.query:
            query.update(options.query)
        
        # Prepare request options
        request_options = LogStatsOptions(
            method="GET",
            query=query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send request
        response = await self.client.send(f"/api/logs/{id}", request_options)
        
        return LogModel(
            id=response.get('id', ''),
            level=response.get('level', ''),
            message=response.get('message', ''),
            created=response.get('created', ''),
            updated=response.get('updated', ''),
            data=response.get('data', {})
        )
    
    async def get_stats(self, options: Optional[LogStatsOptions] = None) -> Dict[str, Any]:
        """
        Fetches log statistics.
        
        Args:
            options: Additional request options
            
        Returns:
            Log statistics
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = LogStatsOptions()
        
        # Build query parameters
        query = {}
        if options.filter:
            query['filter'] = options.filter
        if options.fields:
            query['fields'] = options.fields
        
        # Merge with existing query
        if options.query:
            query.update(options.query)
        
        # Prepare request options
        request_options = LogStatsOptions(
            method="GET",
            query=query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        return await self.client.send("/api/logs/stats", request_options)
    
    async def get_request_logs(
        self,
        page: int = 1,
        per_page: int = 30,
        options: Optional[LogStatsOptions] = None
    ) -> ListResult:
        """
        Fetches HTTP request logs.
        
        Args:
            page: Page number
            per_page: Items per page
            options: Additional request options
            
        Returns:
            Paginated list of request logs
        """
        if options is None:
            options = LogStatsOptions()
        
        # Build query parameters
        query = {
            'page': page,
            'perPage': per_page
        }
        
        if options.sort:
            query['sort'] = options.sort
        if options.filter:
            query['filter'] = options.filter
        if options.fields:
            query['fields'] = options.fields
        
        if options.query:
            query.update(options.query)
        
        # Prepare request options
        request_options = LogStatsOptions(
            method="GET",
            query=query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send request
        response = await self.client.send("/api/logs/requests", request_options)
        
        # Convert to ListResult
        items = response.get('items', [])
        
        return ListResult(
            page=response.get('page', page),
            per_page=response.get('perPage', per_page),
            total_items=response.get('totalItems', 0),
            total_pages=response.get('totalPages', 0),
            items=items
        )
    
    async def get_error_logs(
        self,
        page: int = 1,
        per_page: int = 30,
        options: Optional[LogStatsOptions] = None
    ) -> ListResult:
        """
        Fetches error logs.
        
        Args:
            page: Page number
            per_page: Items per page
            options: Additional request options
            
        Returns:
            Paginated list of error logs
        """
        if options is None:
            options = LogStatsOptions()
        
        # Set filter for error logs
        if not options.filter:
            options.filter = "level != 'debug'"
        else:
            options.filter = f"({options.filter}) && level != 'debug'"
        
        return await self.get_list(page, per_page, options)
    
    async def get_critical_logs(
        self,
        page: int = 1,
        per_page: int = 30,
        options: Optional[LogStatsOptions] = None
    ) -> ListResult:
        """
        Fetches critical error logs.
        
        Args:
            page: Page number
            per_page: Items per page
            options: Additional request options
            
        Returns:
            Paginated list of critical logs
        """
        if options is None:
            options = LogStatsOptions()
        
        # Set filter for critical logs
        if not options.filter:
            options.filter = "level = 'fatal' || level = 'error'"
        else:
            options.filter = f"({options.filter}) && (level = 'fatal' || level = 'error')"
        
        return await self.get_list(page, per_page, options)
    
    async def delete_logs_older_than(
        self,
        days: int,
        options: Optional[LogStatsOptions] = None
    ) -> bool:
        """
        Delete logs older than specified number of days.
        
        Args:
            days: Number of days to keep
            options: Additional request options
            
        Returns:
            True if deletion was successful
            
        Raises:
            ClientResponseError: If deletion fails
        """
        if options is None:
            options = LogStatsOptions()
        
        # Prepare request options
        request_options = LogStatsOptions(
            method="DELETE",
            query={'days': days},
            headers=options.headers,
            request_key=options.request_key
        )
        
        if options.query:
            request_options.query.update(options.query)
        
        await self.client.send("/api/logs/cleanup", request_options)
        return True
