import time
from collections import defaultdict
from fastapi import HTTPException, status, Request
from app.core.config import settings

# In-memory sliding window rate limiter
_request_records = defaultdict(list)

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
        
        # Clean expired timestamps
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

