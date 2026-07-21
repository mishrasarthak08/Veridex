import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models.user import User
from app.db.models.organization import Organization
from app.db.models.workspace import Workspace
from app.db.models.project import Project
from sqlalchemy.future import select

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Check if users already exist
        result = await session.execute(select(User).limit(1))
        existing_user = result.scalars().first()
        
        if existing_user:
            print("Database already seeded!")
            return

        print("Seeding database with dummy data...")

        # 1. Create a User
        user = User(
            email="demo@veridex.ai",
            hashed_password="hashed_dummy_password",  # Just a dummy
            first_name="Demo",
            last_name="User",
            is_active=True,
            is_superuser=True
        )
        session.add(user)
        await session.flush()

        # 2. Create an Organization
        org = Organization(
            name="Veridex Corp",
            description="The default organization for demo purposes."
        )
        session.add(org)
        await session.flush()

        # 3. Create a Workspace
        workspace = Workspace(
            name="Engineering",
            description="Engineering workspace",
            organization_id=org.id
        )
        session.add(workspace)
        await session.flush()

        # 4. Create a Project
        project = Project(
            name="Agent Framework",
            description="Core agent framework project",
            workspace_id=workspace.id
        )
        session.add(project)
        await session.flush()

        await session.commit()
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
