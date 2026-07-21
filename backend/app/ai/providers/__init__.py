from .base import BaseProvider
from app.core.config import settings

class ProviderFactory:
    _providers = None

    @classmethod
    def _init_providers(cls):
        if cls._providers is not None:
            return
            
        cls._providers = {}
        
        if getattr(settings, "OPENAI_API_KEY", None):
            from .openai import OpenAIProvider
            cls._providers["openai"] = OpenAIProvider()
            
        if getattr(settings, "ANTHROPIC_API_KEY", None):
            from .anthropic import AnthropicProvider
            cls._providers["anthropic"] = AnthropicProvider()
            
        if getattr(settings, "GEMINI_API_KEY", None):
            from .gemini import GeminiProvider
            cls._providers["gemini"] = GeminiProvider()
            
        # Ollama usually uses a local URL rather than a key
        try:
            from .ollama import OllamaProvider
            cls._providers["ollama"] = OllamaProvider()
        except Exception:
            pass

    @classmethod
    def get_provider(cls, provider_name: str) -> BaseProvider:
        cls._init_providers()
        if provider_name not in cls._providers:
            raise ValueError(f"Provider {provider_name} is not configured or not supported.")
        return cls._providers[provider_name]
