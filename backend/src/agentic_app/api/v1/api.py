"""API v1 router."""

from fastapi import APIRouter, Depends

from agentic_app.api.v1.endpoints import agents, tasks, nim, rag, api_keys
from agentic_app.core.auth import verify_api_key

api_router = APIRouter(dependencies=[Depends(verify_api_key)])

api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(nim.router, prefix="/nim", tags=["nim"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
