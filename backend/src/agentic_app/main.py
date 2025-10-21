"""Main FastAPI application for the Agentic Application."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from agentic_app.api.v1.api import api_router
from agentic_app.core.config import settings
from agentic_app.core.database import create_tables
from agentic_app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    configure_logging()
    await create_tables()
    logging.info("Agentic Application started successfully")
    
    yield
    
    # Shutdown
    logging.info("Agentic Application shutting down")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Agentic Application with NVIDIA NIM integration",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted host middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.BACKEND_CORS_ORIGINS,
        )

    # Rate limiting middleware
    try:
        from agentic_app.core.rate_limiter import RateLimiterMiddleware

        app.add_middleware(RateLimiterMiddleware)
    except Exception:
        # If middleware cannot be imported, continue without rate limiting
        pass

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_application()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Agentic Application API", "version": "1.0.0"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
