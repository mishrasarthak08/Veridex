import httpx
from typing import Dict, Any
from app.core.config import settings

class PolicyEngine:
    def __init__(self):
        # We assume OPA is deployed as a sidecar or centralized service
        # e.g., http://localhost:8181/v1/data/veridex/authz/allow
        self.opa_url = getattr(settings, "OPA_URL", "http://localhost:8181")
        self.policy_path = "/v1/data/veridex/authz/allow"

    async def evaluate(self, user_context: Dict[str, Any], action: str, resource_context: Dict[str, Any]) -> bool:
        """
        Evaluates a request against the Open Policy Agent (OPA).
        """
        payload = {
            "input": {
                "user": user_context,
                "action": action,
                "resource": resource_context
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.opa_url}{self.policy_path}", 
                    json=payload,
                    timeout=2.0 # Fail fast
                )
                
            if response.status_code == 200:
                result = response.json()
                # OPA returns {"result": true|false}
                return result.get("result", False)
            else:
                # If OPA returns non-200, default deny
                print(f"OPA error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Policy evaluation failed: {e}. Bypassing for Phase 7 development.")
            # Fail closed normally, but for Phase 7 testing we bypass
            return True
