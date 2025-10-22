"""
API endpoints for managing API keys
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from agentic_app.core.database import get_db
from agentic_app.core.auth import require_admin_permission, get_current_api_key
from agentic_app.schemas.api_key import (
    ApiKeyCreate, ApiKeyResponse, ApiKeyWithSecret, ApiKeyUpdate, 
    ApiKeyList, ApiKeyUsage
)
from agentic_app.services.api_key_service import ApiKeyService
from agentic_app.models.api_key import ApiKey

router = APIRouter()


@router.post("/", response_model=ApiKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_api_key: str = Depends(require_admin_permission)
):
    """
    Create a new API key
    
    Requires admin permission.
    """
    api_key_service = ApiKeyService(db)
    
    try:
        db_api_key, actual_key = api_key_service.create_api_key(
            api_key_data, 
            created_by="admin"  # TODO: Get from current user context
        )
        
        return ApiKeyWithSecret(
            id=db_api_key.id,
            name=db_api_key.name,
            description=db_api_key.description,
            key=actual_key,  # Only returned once!
            key_prefix=db_api_key.key_prefix,
            permissions=db_api_key.permissions,
            rate_limit=db_api_key.rate_limit,
            expires_at=db_api_key.expires_at,
            created_at=db_api_key.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create API key: {str(e)}"
        )


@router.get("/", response_model=ApiKeyList)
async def list_api_keys(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    active_only: bool = Query(True, description="Return only active keys"),
    db: Session = Depends(get_db),
    current_api_key: str = Depends(require_admin_permission)
):
    """
    List all API keys with pagination
    
    Requires admin permission.
    """
    api_key_service = ApiKeyService(db)
    
    api_keys, total = api_key_service.list_api_keys(
        skip=skip, 
        limit=limit, 
        active_only=active_only
    )
    
    return ApiKeyList(
        api_keys=[ApiKeyResponse.from_orm(key) for key in api_keys],
        total=total,
        page=skip // limit + 1,
        per_page=limit
    )


@router.get("/{api_key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_api_key: str = Depends(require_admin_permission)
):
    """
    Get details of a specific API key
    
    Requires admin permission.
    """
    api_key_service = ApiKeyService(db)
    
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return ApiKeyResponse.from_orm(api_key)


@router.put("/{api_key_id}", response_model=ApiKeyResponse)
async def update_api_key(
    api_key_id: int,
    update_data: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_api_key: str = Depends(require_admin_permission)
):
    """
    Update an API key
    
    Requires admin permission.
    """
    api_key_service = ApiKeyService(db)
    
    updated_api_key = api_key_service.update_api_key(api_key_id, update_data)
    
    if not updated_api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return ApiKeyResponse.from_orm(updated_api_key)


@router.post("/{api_key_id}/revoke")
async def revoke_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_api_key: str = Depends(require_admin_permission)
):
    """
    Revoke (deactivate) an API key
    
    Requires admin permission.
    """
    api_key_service = ApiKeyService(db)
    
    success = api_key_service.revoke_api_key(api_key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return {"message": "API key revoked successfully"}


@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_api_key: str = Depends(require_admin_permission)
):
    """
    Permanently delete an API key
    
    Requires admin permission.
    """
    api_key_service = ApiKeyService(db)
    
    success = api_key_service.delete_api_key(api_key_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    return {"message": "API key deleted successfully"}


@router.get("/usage/stats", response_model=List[ApiKeyUsage])
async def get_usage_stats(
    db: Session = Depends(get_db),
    current_api_key: str = Depends(require_admin_permission)
):
    """
    Get API key usage statistics
    
    Requires admin permission.
    """
    api_key_service = ApiKeyService(db)
    
    usage_stats = api_key_service.get_usage_stats()
    
    return [
        ApiKeyUsage.from_orm(key) for key in usage_stats
    ]


@router.post("/validate")
async def validate_api_key(
    api_key: str,
    db: Session = Depends(get_db)
):
    """
    Validate an API key (public endpoint for testing)
    
    Returns basic validation info without sensitive data.
    """
    api_key_service = ApiKeyService(db)
    
    db_api_key = api_key_service.validate_api_key(api_key)
    
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    
    return {
        "valid": True,
        "name": db_api_key.name,
        "key_prefix": db_api_key.key_prefix,
        "permissions": db_api_key.permissions,
        "rate_limit": db_api_key.rate_limit,
        "expires_at": db_api_key.expires_at,
        "last_used_at": db_api_key.last_used_at
    }


@router.get("/me/info", response_model=ApiKeyResponse)
async def get_current_api_key_info(
    request,
    current_api_key: str = Depends(get_current_api_key)
):
    """
    Get information about the current API key
    
    Returns info about the API key making the request.
    """
    api_key_obj = getattr(request.state, 'api_key', None)
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key information not available"
        )
    
    return ApiKeyResponse.from_orm(api_key_obj)
