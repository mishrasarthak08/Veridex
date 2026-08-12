from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import event
from sqlalchemy.orm import Session, with_loader_criteria
from app.core.config import settings
from app.db.models.base import Base
from app.core.tenant import get_tenant_id

# Use the pooler URL if available
db_url = settings.DATABASE_URL_POOLER

engine = create_async_engine(
    db_url, 
    echo=False, # Disable echo in production
    pool_size=20,          # Base number of connections
    max_overflow=10,       # Max extra connections if pool is full
    pool_timeout=30,       # Timeout before throwing an error if no connection is available
    pool_pre_ping=True,    # Test connections before using them
    pool_recycle=1800      # Recycle connections after 30 minutes
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@event.listens_for(Session, "do_orm_execute")
def _add_tenant_filter(execute_state):
    # Only apply filter if it's a select, update, or delete
    if execute_state.is_select or execute_state.is_update or execute_state.is_delete:
        # Allow PolicyService and other system queries to bypass tenant filtering
        if execute_state.execution_options.get("include_all_tenants", False):
            return
        tenant_id = get_tenant_id()
        if tenant_id:
            # Apply tenant_id filter to all entities deriving from Base
            execute_state.statement = execute_state.statement.options(
                with_loader_criteria(
                    Base,
                    lambda cls: cls.tenant_id == tenant_id,
                    include_aliases=True
                )
            )

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
