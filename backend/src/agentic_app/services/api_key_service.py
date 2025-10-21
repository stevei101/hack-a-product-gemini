"""
API Key service for managing authentication keys
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.api_key import ApiKey
from ..schemas.api_key import ApiKeyCreate, ApiKeyUpdate, Permission


class ApiKeyService:
    """Service for managing API keys"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_api_key(self) -> Tuple[str, str]:
        """
        Generate a new API key and its hash
        
        Returns:
            Tuple of (api_key, key_hash)
        """
        # Generate a secure random API key (32 bytes = 64 hex chars)
        api_key = secrets.token_hex(32)
        
        # Create hash for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Create prefix for identification (first 8 chars)
        key_prefix = api_key[:8]
        
        return api_key, key_hash, key_prefix
    
    def create_api_key(self, api_key_data: ApiKeyCreate, created_by: Optional[str] = None) -> Tuple[ApiKey, str]:
        """
        Create a new API key
        
        Args:
            api_key_data: API key creation data
            created_by: Username of the creator
            
        Returns:
            Tuple of (ApiKey object, actual API key string)
        """
        # Generate new API key
        api_key, key_hash, key_prefix = self.generate_api_key()
        
        # Calculate expiration date
        expires_at = None
        if api_key_data.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=api_key_data.expires_in_days)
        
        # Create API key record
        db_api_key = ApiKey(
            key_hash=key_hash,
            key_prefix=key_prefix,
            name=api_key_data.name,
            description=api_key_data.description,
            permissions=[p.value for p in api_key_data.permissions],
            rate_limit=api_key_data.rate_limit,
            expires_at=expires_at,
            created_by=created_by
        )
        
        self.db.add(db_api_key)
        self.db.commit()
        self.db.refresh(db_api_key)
        
        return db_api_key, api_key
    
    def get_api_key_by_hash(self, key_hash: str) -> Optional[ApiKey]:
        """Get API key by its hash"""
        return self.db.query(ApiKey).filter(
            and_(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
        ).first()
    
    def get_api_key_by_prefix(self, key_prefix: str) -> Optional[ApiKey]:
        """Get API key by its prefix"""
        return self.db.query(ApiKey).filter(
            and_(ApiKey.key_prefix == key_prefix, ApiKey.is_active == True)
        ).first()
    
    def validate_api_key(self, api_key: str) -> Optional[ApiKey]:
        """
        Validate an API key
        
        Args:
            api_key: The API key to validate
            
        Returns:
            ApiKey object if valid, None otherwise
        """
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Find the API key
        db_api_key = self.get_api_key_by_hash(key_hash)
        
        if not db_api_key:
            return None
        
        # Check if key is valid (active and not expired)
        if not db_api_key.is_valid:
            return None
        
        # Update usage statistics
        db_api_key.update_usage()
        self.db.commit()
        
        return db_api_key
    
    def check_permission(self, api_key: str, required_permission: Permission) -> bool:
        """
        Check if an API key has a specific permission
        
        Args:
            api_key: The API key to check
            required_permission: The permission to check for
            
        Returns:
            True if the key has the permission, False otherwise
        """
        db_api_key = self.validate_api_key(api_key)
        if not db_api_key:
            return False
        
        return db_api_key.has_permission(required_permission.value)
    
    def check_any_permission(self, api_key: str, required_permissions: List[Permission]) -> bool:
        """
        Check if an API key has any of the specified permissions
        
        Args:
            api_key: The API key to check
            required_permissions: List of permissions to check for
            
        Returns:
            True if the key has any of the permissions, False otherwise
        """
        db_api_key = self.validate_api_key(api_key)
        if not db_api_key:
            return False
        
        permission_values = [p.value for p in required_permissions]
        return db_api_key.has_any_permission(permission_values)
    
    def list_api_keys(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> Tuple[List[ApiKey], int]:
        """
        List API keys with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            active_only: Whether to return only active keys
            
        Returns:
            Tuple of (list of API keys, total count)
        """
        query = self.db.query(ApiKey)
        
        if active_only:
            query = query.filter(ApiKey.is_active == True)
        
        total = query.count()
        api_keys = query.offset(skip).limit(limit).all()
        
        return api_keys, total
    
    def update_api_key(self, api_key_id: int, update_data: ApiKeyUpdate) -> Optional[ApiKey]:
        """
        Update an API key
        
        Args:
            api_key_id: ID of the API key to update
            update_data: Update data
            
        Returns:
            Updated ApiKey object or None if not found
        """
        db_api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
        
        if not db_api_key:
            return None
        
        # Update fields if provided
        if update_data.name is not None:
            db_api_key.name = update_data.name
        
        if update_data.description is not None:
            db_api_key.description = update_data.description
        
        if update_data.permissions is not None:
            db_api_key.permissions = [p.value for p in update_data.permissions]
        
        if update_data.rate_limit is not None:
            db_api_key.rate_limit = update_data.rate_limit
        
        if update_data.is_active is not None:
            db_api_key.is_active = update_data.is_active
        
        self.db.commit()
        self.db.refresh(db_api_key)
        
        return db_api_key
    
    def revoke_api_key(self, api_key_id: int) -> bool:
        """
        Revoke (deactivate) an API key
        
        Args:
            api_key_id: ID of the API key to revoke
            
        Returns:
            True if successful, False if key not found
        """
        db_api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
        
        if not db_api_key:
            return False
        
        db_api_key.is_active = False
        self.db.commit()
        
        return True
    
    def delete_api_key(self, api_key_id: int) -> bool:
        """
        Permanently delete an API key
        
        Args:
            api_key_id: ID of the API key to delete
            
        Returns:
            True if successful, False if key not found
        """
        db_api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
        
        if not db_api_key:
            return False
        
        self.db.delete(db_api_key)
        self.db.commit()
        
        return True
    
    def get_usage_stats(self) -> List[ApiKey]:
        """Get API key usage statistics"""
        return self.db.query(ApiKey).filter(ApiKey.is_active == True).all()
