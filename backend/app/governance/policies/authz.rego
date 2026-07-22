package veridex.authz

import future.keywords.in

default allow := false

# Input Schema:
# {
#   "user": {
#     "id": "u123",
#     "roles": ["workspace_admin", "org_member"],
#     "organization_id": "org_1"
#   },
#   "action": "read",
#   "resource": {
#     "type": "document",
#     "id": "doc_456",
#     "organization_id": "org_1",
#     "workspace_id": "ws_789"
#   }
# }

# RBAC Definitions
# This would normally be passed as data to OPA, but for simplicity we define some static role mappings here
# or we can write rules based on generic tenant matching.

# 1. Hard Tenant Isolation: User's org_id MUST match resource's org_id
tenant_match {
    input.user.organization_id == input.resource.organization_id
}

# 2. System Admins can do anything
allow {
    "system_admin" in input.user.roles
}

# 3. Org Admins can do anything within their org
allow {
    tenant_match
    "org_admin" in input.user.roles
}

# 4. Workspace Admins can perform actions on resources in their workspace
allow {
    tenant_match
    "workspace_admin" in input.user.roles
    # In a real setup, we'd verify the user is actually a workspace_admin FOR THIS SPECIFIC workspace.
    # For now, we assume if they have the role, and the org matches, we allow it (simplified).
}

# 5. Members can read resources in their org
allow {
    tenant_match
    input.action == "read"
    "org_member" in input.user.roles
}
