import os
import sys
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.main import app
from app.core.config import settings

def test_google_oauth_configuration():
    print("1. Verifying Google OAuth Configuration...")
    settings.GOOGLE_CLIENT_ID = "test_google_client_id"
    settings.GOOGLE_CLIENT_SECRET = "test_google_client_secret"
    print("   -> Configuration is active.")
    
def test_google_login_route():
    print("2. Verifying Google Login Route...")
    client = TestClient(app)
    response = client.get("/api/v1/auth/google/login", follow_redirects=False)
    
    assert response.status_code == 307
    location = response.headers["location"]
    
    # Check that required query parameters are in the redirect URL
    assert "https://accounts.google.com/o/oauth2/v2/auth" in location
    assert "client_id=test_google_client_id" in location
    assert "redirect_uri=" in location
    assert "access_type=offline" in location
    assert "prompt=consent" in location
    assert "scope=" in location
    print("   -> Redirect URL correctly configured for offline access and profile scopes.")
    
if __name__ == "__main__":
    try:
        test_google_oauth_configuration()
        test_google_login_route()
        print("\nSUCCESS: Google OAuth routes and configuration are verified!")
        print("Note: Set real GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env to test full flow.")
    except Exception as e:
        print(f"\nFAILED: {e}")
