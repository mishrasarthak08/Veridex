import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def main():
    print(f"Connecting to Postgres at {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}...")
    
    engine = create_async_engine(settings.DATABASE_URI, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Test simple connection
            result = await session.execute(text("SELECT 1"))
            val = result.scalar()
            print(f"1. Connection successful! SELECT 1 returned: {val}")
            
            # Test table existence (assuming alembic ran successfully)
            tables_result = await session.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            )
            tables = [row[0] for row in tables_result.fetchall()]
            
            print(f"2. Found {len(tables)} tables in the public schema:")
            for t in tables:
                print(f"   - {t}")
                
            if 'alembic_version' in tables:
                print("3. SUCCESS: Alembic version table found, migrations are working.")
            else:
                print("3. WARNING: Alembic version table not found. Did you run 'uv run alembic upgrade head'?")
                
    except Exception as e:
        print(f"FAILED to verify PostgreSQL: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
