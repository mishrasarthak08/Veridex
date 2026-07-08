from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter()

@router.get("/audit-log")
async def get_audit_log(tenant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Returns the immutable audit log for the compliance dashboard.
    (Mocked response for now)
    """
    return [
        {
            "timestamp": "2026-07-07T12:00:00Z",
            "actor": "admin_123",
            "action": "POLICY_UPDATE",
            "details": {"policy": "finance-agent", "change": "denied send_email"}
        }
    ]

@router.get("/quotas")
async def get_tenant_quotas(tenant_id: str) -> Dict[str, Any]:
    """
    Returns the usage vs quota limits for the given tenant.
    """
    return {
        "tokens_used": 145000,
        "token_limit": 1000000,
        "workflows_active": 12,
        "workflows_limit": 50
    }
