"""
Batch service for transactional operations
"""
from typing import Any, Dict, List, Optional
from .base_service import BaseService
from ..utils.options import SendOptions


class BatchService(BaseService):
    """
    Service for batch transactional operations.
    
    This service allows sending multiple create/update/upsert/delete
    collection requests in a single network call.
    """
    
    def __init__(self, client):
        """
        Initialize batch service.
        
        Args:
            client: PocketBase client instance
        """
        super().__init__(client)
        self._batch_items: List[Dict[str, Any]] = []
    
    @property
    def base_path(self) -> str:
        """Returns base path for batch operations."""
        return "/api/batch"
    
    def collection(self, collection_id_or_name: str):
        """
        Get a batch collection service.
        
        Args:
            collection_id_or_name: Collection ID or name
            
        Returns:
            BatchCollectionService instance
        """
        return BatchCollectionService(self.client, collection_id_or_name, self)
    
    async def send(self, options: Optional[SendOptions] = None) -> List[Any]:
        """
        Execute the batch request.
        
        Args:
            options: Additional request options
            
        Returns:
            List of batch operation results
            
        Raises:
            ClientResponseError: If batch request fails
            ValueError: If no batch items added
        """
        if not self._batch_items:
            raise ValueError("No batch items added")
        
        if options is None:
            options = SendOptions()
        
        # Prepare request options
        request_options = SendOptions(
            method="POST",
            body={"batch": self._batch_items},
            query=options.query,
            headers=options.headers,
            request_key=options.request_key
        )
        
        # Send batch request
        response = await self.client.send(self.base_path, request_options)
        
        # Clear batch items
        self._batch_items.clear()
        
        return response
    
    def add_item(self, collection: str, action: str, body: Dict[str, Any]) -> None:
        """
        Add a batch item.
        
        Args:
            collection: Collection name
            action: Action type (create, update, delete, etc.)
            body: Request body for the action
        """
        self._batch_items.append({
            "collection": collection,
            "action": action,
            "body": body
        })
    
    def clear(self) -> None:
        """Clear all batch items."""
        self._batch_items.clear()
    
    def count(self) -> int:
        """Get number of batch items."""
        return len(self._batch_items)


class BatchCollectionService:
    """
    Service for batch operations on a specific collection.
    
    This service provides methods for adding batch items
    for a specific collection.
    """
    
    def __init__(self, client, collection_id_or_name: str, batch_service: BatchService):
        """
        Initialize batch collection service.
        
        Args:
            client: PocketBase client instance
            collection_id_or_name: Collection ID or name
            batch_service: Parent batch service
        """
        self.client = client
        self.collection_id_or_name = collection_id_or_name
        self.batch_service = batch_service
    
    def create(self, body_params: Dict[str, Any]) -> BatchService:
        """
        Add a create operation to the batch.
        
        Args:
            body_params: Record data to create
            
        Returns:
            The batch service for chaining
        """
        self.batch_service.add_item(self.collection_id_or_name, "create", body_params)
        return self.batch_service
    
    def update(self, id: str, body_params: Dict[str, Any]) -> BatchService:
        """
        Add an update operation to the batch.
        
        Args:
            id: Record ID to update
            body_params: Update data
            
        Returns:
            The batch service for chaining
        """
        self.batch_service.add_item(self.collection_id_or_name, "update", {
            "id": id,
            **body_params
        })
        return self.batch_service
    
    def delete(self, id: str) -> BatchService:
        """
        Add a delete operation to the batch.
        
        Args:
            id: Record ID to delete
            
        Returns:
            The batch service for chaining
        """
        self.batch_service.add_item(self.collection_id_or_name, "delete", {
            "id": id
        })
        return self.batch_service
    
    def upsert(self, body_params: Dict[str, Any]) -> BatchService:
        """
        Add an upsert operation to the batch.
        
        Args:
            body_params: Record data (must include ID for update)
            
        Returns:
            The batch service for chaining
        """
        self.batch_service.add_item(self.collection_id_or_name, "upsert", body_params)
        return self.batch_service
    
    def patch(self, id: str, body_params: Dict[str, Any]) -> BatchService:
        """
        Add a patch operation to the batch.
        
        Args:
            id: Record ID to patch
            body_params: Patch data
            
        Returns:
            The batch service for chaining
        """
        self.batch_service.add_item(self.collection_id_or_name, "patch", {
            "id": id,
            **body_params
        })
        return self.batch_service
