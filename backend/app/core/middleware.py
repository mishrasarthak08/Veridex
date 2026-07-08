import uuid
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate Request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Start timing
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # End timing
        process_time_ms = (time.time() - start_time) * 1000
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f} ms"
        
        # Log request summary
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "latency_ms": round(process_time_ms, 2),
                "endpoint": request.url.path,
                "status": response.status_code,
                "method": request.method,
            }
        )
        
        return response
