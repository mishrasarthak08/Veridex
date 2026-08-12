from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.db.models.oauth import OAuthAccount

class OAuthAccountRepository(BaseRepository[OAuthAccount]):
    def __init__(self, db: AsyncSession):
        super().__init__(OAuthAccount, db)

    async def get_by_provider(self, provider: str, provider_account_id: str) -> Optional[OAuthAccount]:
        stmt = select(OAuthAccount).where(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_account_id == provider_account_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()
