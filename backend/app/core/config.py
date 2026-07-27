from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Veridex"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000", "http://127.0.0.1:3000", "http://0.0.0.0:3000",
        "http://localhost:3001", "http://127.0.0.1:3001",
        "http://localhost:3002", "http://127.0.0.1:3002"
    ]
    
    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "veridex"
    POSTGRES_PASSWORD: str = "veridex_secret"
    POSTGRES_DB: str = "veridex_db"
    POSTGRES_PORT: int = 5432
    # Redis
    REDIS_SERVER: str = "localhost"
    REDIS_PORT: int = 6379
    
    # MinIO
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "veridex-knowledge"
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    
    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "veridex_secret"
    
    # OPA Governance
    OPA_URL: str = "http://localhost:8181"
    
    # Auth
    SECRET_KEY: str = "REPLACE_ME_WITH_STRONG_SECRET_IN_PROD"
    FERNET_SECRET_KEY: str = "gU2b2uB02_sM-m9W7G6Nq1GvH3Y8p2a0R3sM3y1t3lA=" # Default fallback for dev
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15 # 15 minutes for short lived access
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # 7 days for refresh token
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # LLM Providers
    OPENAI_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    
    # Connector Tokens
    GITHUB_TOKEN: str | None = None
    SLACK_BOT_TOKEN: str | None = None
    HANDSHAKE_API_TOKEN: str | None = None
    
    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
    @property
    def DATABASE_URL_POOLER(self) -> str:
        # Use a pooled connection string if provided (e.g. Supabase PgBouncer)
        # Otherwise fallback to the standard URI
        pooler_url = os.environ.get("DATABASE_URL_POOLER")
        if pooler_url:
            if pooler_url.startswith("postgres://"):
                pooler_url = pooler_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif pooler_url.startswith("postgresql://"):
                pooler_url = pooler_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return pooler_url
        return self.DATABASE_URI
    
    @property
    def REDIS_URL(self) -> str:
        # If REDIS_SERVER is already a full URI (e.g. from Upstash or Render)
        if self.REDIS_SERVER.startswith("redis://") or self.REDIS_SERVER.startswith("rediss://"):
            return self.REDIS_SERVER
        return f"redis://{self.REDIS_SERVER}:{self.REDIS_PORT}/0"
    
    # We will look for .env in the parent directory as well
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env"), 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
