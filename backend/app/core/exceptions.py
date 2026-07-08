from fastapi import Request
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
            content=error_response(
                code=exc.code, 
                message=exc.message, 
                details=exc.details
            ).model_dump()
        )
        
    # Unhandled exceptions
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True, extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content=error_response(
            code="INTERNAL_SERVER_ERROR", 
            message="An unexpected error occurred."
        ).model_dump()
    )

def setup_exception_handlers(app):
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(PlatformException, global_exception_handler)
