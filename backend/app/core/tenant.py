import contextvars

# Context variable to store the current tenant_id
tenant_context = contextvars.ContextVar("tenant_context", default="default_tenant")

def get_tenant_id() -> str:
    return tenant_context.get()

def set_tenant_id(tenant_id: str) -> None:
    tenant_context.set(tenant_id)
