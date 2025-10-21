"""Simple in-memory rate limiting middleware.

This implements a fixed-window counter per identifier (X-API-Key if present, else client IP).
It's intended as a lightweight protection for development and small deployments. For
production or multi-process deployments, replace with a Redis-based shared limiter.
"""
import hashlib
import time

import redis.asyncio as redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from agentic_app.core.config import settings


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Redis-based rate limiter using a fixed-window algorithm."""

    def __init__(self, app, requests: int | None = None, window_seconds: int | None = None):
        super().__init__(app)
        self.requests = requests or settings.RATE_LIMIT_DEFAULT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW_SECONDS
        self.redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Generate a unique identifier for the client
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # Hash the API key for security
            identifier = hashlib.sha256(api_key.encode()).hexdigest()
        else:
            # Fallback to IP address
            xff = request.headers.get("x-forwarded-for")
            ip = xff.split(",")[0].strip() if xff else request.client.host or "unknown"
            identifier = ip

        key = f"rate_limit:{identifier}"

        # Use a Redis pipeline for atomic operations
        async with self.redis_client.pipeline() as pipe:
            pipe.incr(key)
            pipe.expire(key, self.window_seconds)
            result = await pipe.execute()
            count = result[0]

        remaining = self.requests - count
        
        if count > self.requests:
            # Determine the remaining time for the window
            ttl = await self.redis_client.ttl(key)
            retry_after = max(ttl, 1)  # Ensure retry_after is at least 1
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded", "retry_after": retry_after},
                headers={"Retry-After": str(retry_after)},
            )

        # Attach rate limit info to request.state
        request.state.rate_limit = {
            "limit": self.requests,
            "remaining": remaining,
            "window_seconds": self.window_seconds,
        }

        response: Response = await call_next(request)

        # Add headers to responses
        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Window-Seconds"] = str(self.window_seconds)

        return response
