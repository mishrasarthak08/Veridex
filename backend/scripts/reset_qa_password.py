import asyncio
from app.db.session import AsyncSessionLocal
from app.db.models import User
from app.core.security import get_password_hash
from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == 'qa_tester@veridex.io').execution_options(include_all_tenants=True))
        user = result.scalars().first()
        if user:
            user.hashed_password = get_password_hash('admin123')
            await db.commit()
            print("Updated password to admin123")
        else:
            print("User not found!")

asyncio.run(main())
