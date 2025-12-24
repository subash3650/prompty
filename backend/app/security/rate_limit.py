"""Rate limiting middleware and decorators."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import get_settings


settings = get_settings()

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded response."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please wait before trying again.",
            "retry_after": str(exc.detail)
        }
    )


# Common rate limit strings
RATE_LIMIT_GAME = f"{settings.rate_limit_per_minute}/minute"  # 10 prompts/min
RATE_LIMIT_AUTH = "5/minute"  # 5 login attempts/min
RATE_LIMIT_GENERAL = "60/minute"  # 60 requests/min for general endpoints
