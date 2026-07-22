from typing import TypeVar, Generic, Type, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.multitenant import MultiTenantBase

ModelType = TypeVar("ModelType", bound=MultiTenantBase)

class BaseTenantRepository(Generic[ModelType]):
    """
    Base repository for all multi-tenant domain models.
    Enforces that every query and mutation is scoped to a specific tenant_id.
    """
    def __init__(self, model: Type[ModelType], session: AsyncSession, tenant_id: str):
        self.model = model
        self.session = session
        self.tenant_id = tenant_id
        
    def _scope_query(self, stmt):
        """Automatically scopes every query to the current tenant_id."""
        return stmt.where(self.model.tenant_id == self.tenant_id)

    async def get(self, id: Any) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        stmt = self._scope_query(stmt)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        stmt = self._scope_query(stmt)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: dict) -> ModelType:
        # Hard-code the tenant_id on creation to prevent spoofing
        obj_in["tenant_id"] = self.tenant_id
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        # Do not allow tenant_id updates
        if "tenant_id" in obj_in:
            del obj_in["tenant_id"]
            
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
            
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj
