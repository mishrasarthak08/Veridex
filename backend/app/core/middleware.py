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
import jwt
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.services.policy_service import PolicyService
from app.governance.audit import ImmutableAuditLog

class OPAMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.policy_service = PolicyService()
        self.audit_log = ImmutableAuditLog()
        
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # We only protect API routes
        if not path.startswith("/api/"):
            return await call_next(request)
            
        # Bypass public auth routes
        if path.startswith("/api/v1/auth/"):
            return await call_next(request)
            
        # Bypass health routes
        if path.startswith("/api/v1/health/"):
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid authorization header"})
            
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if not user_id:
                return JSONResponse(status_code=401, content={"detail": "Invalid token payload"})
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": "Could not validate credentials"})
            
        # Map path to resource (e.g. /api/v1/projects -> project)
        parts = path.split("/")
        resource = "unknown"
        if len(parts) >= 4:
            resource = parts[3] # e.g. projects, evaluations
            # Basic singularization for typical REST resources
            if resource.endswith("s"):
                resource = resource[:-1]
                
        # Map method to action
        method = request.method.upper()
        if method == "GET":
            action = "read"
        elif method == "DELETE":
            action = "delete"
        else:
            action = "write"
            
        async with AsyncSessionLocal() as db:
            decision = await self.policy_service.evaluate(db, user_id, resource, action)
            
            # Log the governance decision
            await self.audit_log.log_action(
                tenant_id="default_tenant",
                actor=str(user_id),
                action=action,
                resource=resource,
                details={"path": path, "method": method, "policy_reason": decision.reason},
                decision="ALLOW" if decision.allow else "DENY",
                policy_id=decision.policy_id
            )
            
            if not decision.allow:
                logger.warning(f"Policy Engine Denied access for {user_id} on {action} {resource} (Path: {path})")
                return JSONResponse(status_code=403, content={"detail": f"Forbidden by policy: {decision.reason}"})
                
        # Inject user_id into state for downstream routes
        request.state.user_id = user_id
        
        return await call_next(request)
