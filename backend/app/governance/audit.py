import json
from datetime import datetime, timezone
import aiofiles

class ImmutableAuditLog:
    """
    Append-only ledger for all significant AI and human actions.
    """
    def __init__(self, log_path: str = "audit_trail.jsonl"):
        self.log_path = log_path

    async def log_action(self, tenant_id: str, actor: str, action: str, resource: str, details: dict, decision: str = "ALLOW", policy_id: str = "none"):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id,
            "actor": actor,
            "action": action,
            "resource": resource,
            "decision": decision,
            "policy_id": policy_id,
            "details": details
        }
        async with aiofiles.open(self.log_path, mode='a') as f:
            await f.write(json.dumps(log_entry) + "\n")
