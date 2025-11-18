"""
CRUD service for basic database operations
"""
from typing import Any, Dict, List, Optional, Union
from .base_service import BaseService
from src.pocketbase_sdk.utils.dtos import ListResult
from src.pocketbase_sdk.utils.options import (
    CommonOptions, ListOptions, FullListOptions
)


class CrudService(BaseService):
    """
    Basic CRUD operations service.
    
    This service provides common Create, Read, Update, Delete operations
    for collections and records.
    """
    
    @property
    def base_crud_path(self) -> str:
        """
        Must return the service base crud path.
        
        Returns:
            Base path for CRUD operations
        """
        raise NotImplementedError("base_crud_path must be implemented")
    
    def decode(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode a response model.
        
        Args:
            data: Raw response data
            
        Returns:
            Decoded data
        """
        return data
    
    async def get_list(
        self,
        page: int = 1,
        per_page: int = 30,
        options: Optional[ListOptions] = None
    ) -> ListResult:
        """
        Fetches a paginated list of records.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 30)
            options: Additional request options
            
        Returns:
            Paginated list result
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = ListOptions()
        
        # Build query parameters
        query = {
            'page': page,
            'perPage': per_page
        }
        
        # Add option-specific query params
        if options.page is not None:
            query['page'] = options.page
        if options.per_page is not None:
            query['perPage'] = options.per_page
        if options.sort:
            query['sort'] = options.sort
        if options.filter:
            query['filter'] = options.filter
        if options.skip_total is not None:
            query['skipTotal'] = str(options.skip_total).lower()
        if options.fields:
            query['fields'] = options.fields
        
        # Merge with existing query
        if options.query:
            query.update(options.query)
        
        # Prepare request options
        request_options = CommonOptions(
            method="GET",
            query=query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send request
        response = await self.client.send(self.base_crud_path, request_options)
        
        # Convert to ListResult
        return ListResult(
            page=response.get('page', page),
            per_page=response.get('perPage', per_page),
            total_items=response.get('totalItems', 0),
            total_pages=response.get('totalPages', 0),
            items=[self.decode(item) for item in response.get('items', [])]
        )
    
    async def get_first_list_item(
        self,
        filter_expr: str,
        options: Optional[ListOptions] = None
    ) -> Dict[str, Any]:
        """
        Fetches the first matching item.
        
        Args:
            filter_expr: Filter expression
            options: Additional request options
            
        Returns:
            First matching item
            
        Raises:
            ClientResponseError: If request fails or no items found
        """
        if options is None:
            options = ListOptions()
        
        # Build query parameters
        query = {'filter': filter_expr}
        
        # Add existing query params
        if options.query:
            query.update(options.query)
        
        # Use filter to get first item
        request_options = CommonOptions(
            method="GET",
            query=query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send request
        response = await self.client.send(f"{self.base_crud_path}?filter={filter_expr}", request_options)
        
        items = response.get('items', [])
        if not items:
            raise ValueError("No items found matching the filter")
        
        return self.decode(items[0])
    
    async def get_full_list(
        self,
        batch: int = 200,
        options: Optional[FullListOptions] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches all records, batching requests if needed.
        
        Args:
            batch: Batch size for requests (default: 200)
            options: Additional request options
            
        Returns:
            List of all records
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = FullListOptions()
        
        result: List[Dict[str, Any]] = []
        current_page = 1
        has_more = True
        
        while has_more:
            # Build options for this batch
            batch_options = ListOptions(
                page=current_page,
                per_page=batch,
                sort=options.sort,
                filter=options.filter,
                fields=options.fields,
                skip_total=True,  # We don't need total count for batching
                headers=options.headers,
                request_key=options.request_key
            )
            
            # Merge query params
            if options.query:
                batch_options.query.update(options.query)
            
            # Get batch
            list_result = await self.get_list(current_page, batch, batch_options)
            
            # Add to result
            result.extend(list_result.items)
            
            # Check if there are more items
            has_more = len(list_result.items) == batch
            current_page += 1
            
            # Safety check to prevent infinite loop
            if current_page > 1000:
                break
        
        return result
    
    async def get_one(
        self,
        id: str,
        options: Optional[CommonOptions] = None
    ) -> Dict[str, Any]:
        """
        Fetches a single record by its ID.
        
        Args:
            id: Record ID
            options: Additional request options
            
        Returns:
            Record data
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = CommonOptions()
        
        # Build query parameters
        query = {}
        if options.fields:
            query['fields'] = options.fields
        
        # Merge with existing query
        if options.query:
            query.update(options.query)
        
        # Prepare request options
        request_options = CommonOptions(
            method="GET",
            query=query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send request
        response = await self.client.send(f"{self.base_crud_path}/{id}", request_options)
        return self.decode(response)
    
    async def create(
        self,
        body_params: Optional[Union[Dict[str, Any], Any]] = None,
        options: Optional[CommonOptions] = None
    ) -> Dict[str, Any]:
        """
        Creates a new record.
        
        Args:
            body_params: Record data
            options: Additional request options
            
        Returns:
            Created record
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = CommonOptions()
        
        # Build query parameters
        query = {}
        if options.fields:
            query['fields'] = options.fields
        
        # Merge with existing query
        if options.query:
            query.update(options.query)
        
        # Prepare request options
        request_options = CommonOptions(
            method="POST",
            body=body_params or {},
            query=query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send request
        response = await self.client.send(self.base_crud_path, request_options)
        return self.decode(response)
    
    async def update(
        self,
        id: str,
        body_params: Optional[Union[Dict[str, Any], Any]] = None,
        options: Optional[CommonOptions] = None
    ) -> Dict[str, Any]:
        """
        Updates an existing record.
        
        Args:
            id: Record ID
            body_params: Updated record data
            options: Additional request options
            
        Returns:
            Updated record
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = CommonOptions()
        
        # Build query parameters
        query = {}
        if options.fields:
            query['fields'] = options.fields
        
        # Merge with existing query
        if options.query:
            query.update(options.query)
        
        # Prepare request options
        request_options = CommonOptions(
            method="PATCH",
            body=body_params or {},
            query=query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send request
        response = await self.client.send(f"{self.base_crud_path}/{id}", request_options)
        return self.decode(response)
    
    async def delete(
        self,
        id: str,
        options: Optional[CommonOptions] = None
    ) -> bool:
        """
        Deletes a single record by its ID.
        
        Args:
            id: Record ID
            options: Additional request options
            
        Returns:
            True if deletion was successful
            
        Raises:
            ClientResponseError: If request fails
        """
        if options is None:
            options = CommonOptions()
        
        # Prepare request options
        request_options = CommonOptions(
            method="DELETE",
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send request
        await self.client.send(f"{self.base_crud_path}/{id}", request_options)
        return True
