import time
from collections import defaultdict
from typing import Optional
from fastapi import HTTPException, status, Request
from app.core.config import settings
from app.core.observability import logger

# In-memory sliding window rate limiter fallback
_request_records = defaultdict(list)

# Optional Redis connection cache
_redis_client = None
_redis_checked = False

def _get_redis_client():
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    _redis_checked = True
    if settings.REDIS_URL:
        try:
            import redis
            client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1.0)
            client.ping()
            _redis_client = client
            logger.info("Distributed Redis rate limiter connected.")
        except Exception as e:
            logger.warning(f"Redis rate limiter connection failed ({e}); using in-memory sliding window.")
            _redis_client = None
    return _redis_client

def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    async def dependency(request: Request):
        if settings.APP_ENV == "test":
            return True

        # Extract client IP, prioritizing X-Forwarded-For if available
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "127.0.0.1"

        now = time.time()
        
        # Check if Redis distributed limiter is active
        r = _get_redis_client()
        if r:
            try:
                key = f"rate_limit:{client_ip}:{window_seconds}"
                pipe = r.pipeline()
                pipe.zremrangebyscore(key, 0, now - window_seconds)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, window_seconds)
                _, _, count, _ = pipe.execute()
                if count > max_requests:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded. Please try again later."
                    )
                return True
            except HTTPException:
                raise
            except Exception as e:
                logger.warning(f"Redis rate limiting error ({e}); falling back to in-memory.")

        # In-memory sliding window fallback
        timestamps = _request_records[client_ip]
        _request_records[client_ip] = [ts for ts in timestamps if now - ts < window_seconds]
        
        if len(_request_records[client_ip]) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        _request_records[client_ip].append(now)
        return True
    return dependency

