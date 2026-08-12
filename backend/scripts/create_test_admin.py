import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.session import AsyncSessionLocal
from app.db.models import User, Role
from app.core.security import get_password_hash
from sqlalchemy.future import select

async def main():
    async with AsyncSessionLocal() as db:
        # Check if qa_admin exists
        result = await db.execute(select(User).where(User.email == 'qa_admin@veridex.io').execution_options(include_all_tenants=True))
        user = result.scalars().first()
        if not user:
            user = User(
                email='qa_admin@veridex.io',
                hashed_password=get_password_hash('admin123'),
                first_name='QA',
                last_name='Admin',
                is_active=True,
                is_superuser=True
            )
            db.add(user)
            await db.flush()
        else:
            user.hashed_password = get_password_hash('admin123')
            
        # Get owner role
        result = await db.execute(select(Role).where(Role.name == 'owner').execution_options(include_all_tenants=True))
        owner_role = result.scalars().first()
        if owner_role and owner_role not in user.roles:
            user.roles.append(owner_role)
            
        await db.commit()
        print("Test admin created successfully.")

asyncio.run(main())
