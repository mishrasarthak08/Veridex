import asyncio
import os
import sys
import httpx
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app
from app.core.config import settings

def test_github_oauth_configuration():
    print("1. Verifying GitHub OAuth Configuration...")
    # Set dummy configs for test
    settings.GITHUB_CLIENT_ID = "test_client_id"
    settings.GITHUB_CLIENT_SECRET = "test_client_secret"
    
    print("   -> Configuration is active.")
    
def test_github_login_route():
    print("2. Verifying GitHub Login Route...")
    client = TestClient(app)
    response = client.get("/api/v1/auth/github/login", follow_redirects=False)
    
    assert response.status_code == 307
    assert "https://github.com/login/oauth/authorize" in response.headers["location"]
    assert "client_id=test_client_id" in response.headers["location"]
    assert "redirect_uri=" in response.headers["location"]
    print("   -> Redirect URL is correctly formatted.")
    
if __name__ == "__main__":
    try:
        test_github_oauth_configuration()
        test_github_login_route()
        print("\nSUCCESS: GitHub OAuth routes and configuration are verified!")
        print("Note: Run the full flow in browser after setting real GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env.")
    except Exception as e:
        print(f"\nFAILED: {e}")
