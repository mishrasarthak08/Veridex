import asyncio
import os
import sys

# Ensure we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai.providers.openai import OpenAIProvider
from app.core.config import settings

async def main():
    print(f"Loaded OPENAI_API_KEY: {'[SET]' if settings.OPENAI_API_KEY else '[NOT SET]'}")
    if not settings.OPENAI_API_KEY:
        print("ERROR: Please set OPENAI_API_KEY in your .env file before running.")
        sys.exit(1)
        
    provider = OpenAIProvider()
    print("\nExecuting real request to OpenAI (gpt-4o-mini)...")
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France? Please respond in one word."}
    ]
    
    try:
        response = await provider.generate(model="gpt-4o-mini", messages=messages)
        print("\nSuccess! Response received:")
        print("-" * 40)
        print(response["choices"][0]["message"]["content"])
        print("-" * 40)
        print(f"Token Usage: {response['usage']}")
    except Exception as e:
        print(f"\nFailed to communicate with OpenAI: {e}")

if __name__ == "__main__":
    asyncio.run(main())
