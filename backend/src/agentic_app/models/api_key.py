"""
API Key model for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import String, DateTime, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class ApiKey(Base):
    """API Key model for authentication and authorization"""
    
    __tablename__ = "api_keys"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    key_prefix: Mapped[str] = mapped_column(String(10), index=True)  # First 8 chars for identification
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    permissions: Mapped[list[str]] = mapped_column(String(50), default=["read"])  # JSON array of permissions
    rate_limit: Mapped[int] = mapped_column(Integer, default=1000)  # Requests per hour
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Usage tracking
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    
    def __repr__(self) -> str:
        return f"<ApiKey(id={self.id}, name='{self.name}', prefix='{self.key_prefix}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if the API key is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if the API key is valid (active and not expired)"""
        return self.is_active and not self.is_expired
    
    def has_permission(self, permission: str) -> bool:
        """Check if the API key has a specific permission"""
        return permission in self.permissions
    
    def has_any_permission(self, permissions: list[str]) -> bool:
        """Check if the API key has any of the specified permissions"""
        return any(permission in self.permissions for permission in permissions)
    
    def update_usage(self) -> None:
        """Update usage statistics"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
