from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

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

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
