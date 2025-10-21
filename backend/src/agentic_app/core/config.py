"""Application configuration settings."""

import secrets
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    API_KEY: str = ""  # For API authentication

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v:
            raise ValueError("SECRET_KEY environment variable is required")
        return v

    @field_validator("API_KEY", mode="before")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v:
            raise ValueError("API_KEY environment variable is required")
        return v
    SERVER_NAME: Optional[str] = None
    SERVER_HOST: AnyHttpUrl = "http://localhost"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000", "http://localhost:8080"]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "Agentic Application"
    SENTRY_DSN: Optional[HttpUrl] = None

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "agentic_app"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("POSTGRES_PASSWORD", mode="before")
    @classmethod
    def validate_postgres_password(cls, v: str) -> str:
        if not v:
            raise ValueError("POSTGRES_PASSWORD environment variable is required")
        return v

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        values = info.data

        # Build connection string from environment variables or class defaults.
        # Avoid importing `settings` here to prevent circular imports during
        # Settings() initialization.
        import os

        user = os.getenv("POSTGRES_USER", values.get("POSTGRES_USER"))
        password = os.getenv("POSTGRES_PASSWORD", values.get("POSTGRES_PASSWORD"))
        host = os.getenv("POSTGRES_SERVER", values.get("POSTGRES_SERVER"))
        port = os.getenv("POSTGRES_PORT", str(values.get("POSTGRES_PORT")))
        db = os.getenv("POSTGRES_DB", values.get("POSTGRES_DB"))

        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=user,
            password=password,
            host=host,
            port=int(port),
            path=f"/{db}",
        ))

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # NVIDIA NIM Configuration (Hackathon Compliant)
    NIM_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NIM_API_KEY: str = ""
    NIM_MODEL_NAME: str = "nvidia/llama-3_1-nemotron-nano-8b-v1"
    NIM_EMBEDDING_MODEL: str = "nvidia/nv-embedqa-e5-v5"

    @field_validator("NIM_API_KEY", mode="before")
    @classmethod
    def validate_nim_api_key(cls, v: str) -> str:
        if not v:
            raise ValueError("NIM_API_KEY environment variable is required")
        return v

    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = 10
    AGENT_TIMEOUT_SECONDS: int = 300
    MAX_TASK_RETRIES: int = 3

    # Vector Database
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    EMBEDDING_DIMENSION: int = 1024

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    # Default number of requests allowed in the window when no API key-specific limit exists
    RATE_LIMIT_DEFAULT_REQUESTS: int = 100
    # Window duration in seconds for the default rate limit
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
