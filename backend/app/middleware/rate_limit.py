import time
import redis.asyncio as redis
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None

    async def dispatch(self, request: Request, call_next):
        # Initialize Redis client if not already done
        if self.redis_client is None:
            self.redis_client = redis.from_url(settings.redis_url)
        
        # Get client IP
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Create rate limit key
        key = f"rate_limit:{client_ip}"
        
        try:
            # Check current count
            current_count = await self.redis_client.get(key)
            
            if current_count is None:
                # First request in window
                await self.redis_client.setex(
                    key, 
                    settings.rate_limit_window, 
                    1
                )
            else:
                # Increment count
                new_count = int(current_count) + 1
                
                if new_count > settings.rate_limit_requests:
                    # Rate limit exceeded
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded. Please try again later."
                    )
                
                # Update count with expiration
                await self.redis_client.setex(
                    key,
                    settings.rate_limit_window,
                    new_count
                )
        
        except redis.RedisError:
            # If Redis is unavailable, allow the request
            pass
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
        response.headers["X-RateLimit-Window"] = str(settings.rate_limit_window)
        
        current_count = await self.redis_client.get(key)
        if current_count:
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, settings.rate_limit_requests - int(current_count))
            )
        
        return response
