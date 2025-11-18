"""
Local authentication store that persists data
"""
import json
from pathlib import Path
from typing import Optional
from .base_auth_store import BaseAuthStore, AuthRecord
from src.pocketbase_sdk.utils.dtos import RecordModel


class LocalAuthStore(BaseAuthStore):
    """
    AuthStore that persists the auth state in a local file.
    
    By default it stores the data in the user's home directory
    under `.pocketbase_auth.json`.
    """
    
    def __init__(self, storage_path: Optional[str] = None, key: str = "pb_auth"):
        """
        Initialize the local auth store.
        
        Args:
            storage_path: Path to the storage file. If None, uses default location.
            key: Key for storing the auth data in the file
        """
        super().__init__()
        
        self._key = key
        
        if storage_path:
            self._storage_path = Path(storage_path)
        else:
            # Default to user home directory
            home = Path.home()
            self._storage_path = home / ".pocketbase_auth.json"
        
        # Load existing data
        self._load()
    
    def save(self, token: str, record: AuthRecord = None) -> None:
        """
        Saves the provided new token and model data in the auth store.
        
        Args:
            token: Authentication token
            record: Auth record data
        """
        super().save(token, record)
        self._persist()
    
    def clear(self) -> None:
        """Removes the stored token and model data from the auth store."""
        super().clear()
        self._persist()
    
    def _load(self) -> None:
        """Load auth data from storage file."""
        try:
            if not self._storage_path.exists():
                # Create empty file if it doesn't exist
                self._storage_path.parent.mkdir(parents=True, exist_ok=True)
                self._storage_path.write_text("{}")
                return
            
            data_str = self._storage_path.read_text(encoding='utf-8')
            data = json.loads(data_str) if data_str.strip() else {}
            
            # Extract data for this key
            auth_data = data.get(self._key, {})
            
            # Reconstruct record object if present
            record_data = auth_data.get("record")
            record = None
            if record_data and isinstance(record_data, dict):
                # Create RecordModel instance with dynamic attributes
                record = RecordModel(
                    id=record_data.get("id", ""),
                    collection_id=record_data.get("collectionId", ""),
                    collection_name=record_data.get("collectionName", "")
                )
                
                # Add additional fields
                for key, value in record_data.items():
                    if key not in ["id", "collectionId", "collectionName"]:
                        setattr(record, key, value)
            
            # Load into parent
            self._base_token = auth_data.get("token", "")
            self._base_model = record
            
        except Exception:
            # If loading fails, initialize empty state
            self._base_token = ""
            self._base_model = None
    
    def _persist(self) -> None:
        """Persist current auth data to storage file."""
        try:
            # Ensure directory exists
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing data
            data = {}
            if self._storage_path.exists():
                existing_data = self._storage_path.read_text(encoding='utf-8')
                if existing_data.strip():
                    try:
                        data = json.loads(existing_data)
                    except json.JSONDecodeError:
                        data = {}
            
            # Prepare auth data for this key
            auth_data = {
                "token": self._base_token,
                "record": None
            }
            
            if self._base_model:
                # Convert record to dict
                record_dict = self._base_model.__dict__.copy()
                if "_extra_fields" in record_dict:
                    # Merge extra fields into the record dict
                    extra_fields = record_dict.pop("_extra_fields")
                    record_dict.update(extra_fields)
                
                auth_data["record"] = record_dict
            
            # Update data
            data[self._key] = auth_data
            
            # Write to file
            self._storage_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
            
        except Exception:
            # Silently fail to avoid breaking auth operations
            pass
    
    def export_to_file(self, file_path: str) -> bool:
        """
        Export current auth state to a specific file.
        
        Args:
            file_path: Path to export file
            
        Returns:
            True if export succeeded, False otherwise
        """
        try:
            auth_data = {
                "token": self._base_token,
                "record": None
            }
            
            if self._base_model:
                record_dict = self._base_model.__dict__.copy()
                if "_extra_fields" in record_dict:
                    extra_fields = record_dict.pop("_extra_fields")
                    record_dict.update(extra_fields)
                auth_data["record"] = record_dict
            
            export_path = Path(file_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)
            export_path.write_text(json.dumps(auth_data, indent=2), encoding='utf-8')
            
            return True
        except Exception:
            return False
    
    def import_from_file(self, file_path: str) -> bool:
        """
        Import auth state from a specific file.
        
        Args:
            file_path: Path to import file
            
        Returns:
            True if import succeeded, False otherwise
        """
        try:
            import_path = Path(file_path)
            if not import_path.exists():
                return False
            
            data_str = import_path.read_text(encoding='utf-8')
            auth_data = json.loads(data_str)
            
            # Extract data
            token = auth_data.get("token", "")
            record_data = auth_data.get("record")
            
            # Reconstruct record
            record = None
            if record_data and isinstance(record_data, dict):
                record = RecordModel(
                    id=record_data.get("id", ""),
                    collection_id=record_data.get("collectionId", ""),
                    collection_name=record_data.get("collectionName", "")
                )
                
                for key, value in record_data.items():
                    if key not in ["id", "collectionId", "collectionName"]:
                        setattr(record, key, value)
            
            # Save to store
            super().save(token, record)
            self._persist()
            
            return True
        except Exception:
            return False
