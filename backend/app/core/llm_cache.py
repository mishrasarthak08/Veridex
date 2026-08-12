import litellm
from urllib.parse import urlparse
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def setup_llm_cache():
    """
    Initializes Semantic Caching using LiteLLM and Redis.
    This saves LLM API costs and reduces latency for identical or semantically similar queries.
    """
    try:
        redis_url = settings.REDIS_URL
        parsed = urlparse(redis_url)
        
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        password = parsed.password or ""
        
        # We check if OPENAI_API_KEY is available because Litellm defaults to openai for embedding in semantic cache
        if settings.OPENAI_API_KEY:
            import os
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
            
        # Configure litellm to use redis-semantic caching
        litellm.cache = litellm.Cache(
            type="redis-semantic", 
            host=host, 
            port=port, 
            password=password
        )
        logger.info(f"Initialized LiteLLM Redis Semantic Cache at {host}:{port}")
    except Exception as e:
        logger.error(f"Failed to initialize LiteLLM cache: {e}")
