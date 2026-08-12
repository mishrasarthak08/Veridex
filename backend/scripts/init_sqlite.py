import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.session import engine
from app.db.models.base import Base

from app.main import app

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("SQLite tables created.")

if __name__ == "__main__":
    asyncio.run(init_models())
