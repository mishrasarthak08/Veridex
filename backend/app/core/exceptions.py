from fastapi import Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from app.schemas.common import error_response

logger = logging.getLogger(__name__)

class PlatformException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: dict = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details

async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    
    if isinstance(exc, PlatformException):
        logger.warning(f"Platform Exception: {exc.message}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.details or {},
                "request_id": request_id
            }
        )
        
    if isinstance(exc, HTTPException):
        logger.warning(f"HTTP Exception: {exc.detail}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
                "detail": {},
                "request_id": request_id
            }
        )
        
    if isinstance(exc, RequestValidationError):
        logger.warning(f"Validation Error: {exc.errors()}", extra={"request_id": request_id})
        return JSONResponse(
            status_code=422,
            content={
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data.",
                "detail": {"errors": exc.errors()},
                "request_id": request_id
            }
        )
        
    # Unhandled exceptions
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True, extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "detail": {},
            "request_id": request_id
        }
    )

from slowapi.errors import RateLimitExceeded

def setup_exception_handlers(app):
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(PlatformException, global_exception_handler)
    app.add_exception_handler(HTTPException, global_exception_handler)
    app.add_exception_handler(RequestValidationError, global_exception_handler)
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        request_id = getattr(request.state, "request_id", "unknown")
        return JSONResponse(
            status_code=429,
            content={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests, please try again later.",
                "detail": {"error": str(exc.detail)},
                "request_id": request_id
            }
        )
