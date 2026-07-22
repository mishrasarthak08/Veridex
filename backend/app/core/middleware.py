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

from fastapi.responses import JSONResponse
from app.governance.engine import PolicyEngine

class OPAMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.policy_engine = PolicyEngine()
        
    async def dispatch(self, request: Request, call_next):
        # We only protect API routes
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
            
        # In a real app, user_context would be populated by an Authentication middleware (e.g. JWT validation)
        # For this phase, we mock the user context if not present in request.state
        if not hasattr(request.state, "user"):
            # Mock admin user for demonstration purposes, normally this blocks if no user
            request.state.user = {
                "id": "u_dev",
                "roles": ["system_admin"],
                "organization_id": "org_default"
            }
            
        user_context = request.state.user
        action = request.method.lower()
        
        # We can pass path params or query params as resource context
        # Or parse the URL to determine resource type
        resource_context = {
            "type": "api_endpoint",
            "path": request.url.path,
            # For strict tenancy, we assume the resource org matches the user org unless specified
            "organization_id": user_context.get("organization_id")
        }
        
        allowed = await self.policy_engine.evaluate(user_context, action, resource_context)
        
        if not allowed:
            logger.warning(f"OPA Denied access for {user_context.get('id')} on {action} {request.url.path}")
            return JSONResponse(status_code=403, content={"detail": "Forbidden by OPA Policy"})
            
        return await call_next(request)
