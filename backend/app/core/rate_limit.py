from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from fastapi import Request
from app.core.config import settings

def get_user_or_ip(request: Request) -> str:
    # If the user is authenticated (attached by RequestContextMiddleware)
    if hasattr(request.state, "user") and request.state.user:
        return str(request.state.user.id)
    # Fallback to IP address
    return get_remote_address(request)

# Use Redis storage for rate limiting, fallback to memory if REDIS_URL is invalid/not set
if settings.REDIS_SERVER == "localhost":
    limiter = Limiter(
        key_func=get_user_or_ip,
        headers_enabled=True,
        storage_uri="memory://"
    )
else:
    try:
        limiter = Limiter(
            key_func=get_user_or_ip,
            storage_uri=settings.REDIS_URL,
            headers_enabled=True
        )
    except Exception:
        limiter = Limiter(
            key_func=get_user_or_ip,
            headers_enabled=True,
            storage_uri="memory://"
        )
