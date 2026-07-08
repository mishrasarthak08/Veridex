from fastapi import Request, HTTPException

class APIGatewayMiddleware:
    """
    Simulates a centralized API Gateway handling Rate Limiting,
    Quotas, and Auth validation.
    """
    async def validate_request(self, request: Request):
        # 1. Quota Check (Mock)
        # 2. Rate Limit (Mock)
        # 3. Auth Extraction
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            raise HTTPException(status_code=401, detail="Missing Tenant ID")
        return tenant_id
