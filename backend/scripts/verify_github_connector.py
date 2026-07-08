import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.knowledge.connectors.github import GitHubConnector

async def verify_github_connector():
    print("1. Initializing GitHub Connector...")
    # NOTE: To run this against private repos or bypass rate limits, supply a real PAT.
    # For this verification script against a public repo without auth, we can use a dummy token, 
    # but the API might fail due to rate limits or 401s if the token is invalid.
    # We will test against a well-known public repo (e.g., octocat/Hello-World).
    # Since authenticate() uses the /user endpoint which requires a real token, 
    # we'll mock the token validation if the real one isn't provided.
    
    token = os.environ.get("GITHUB_TOKEN", "dummy_token")
    repo = "octocat/Hello-World"
    
    connector = GitHubConnector(access_token=token, repository_full_name=repo)
    
    # We'll skip authenticate() if it's a dummy token because it will definitely fail 401.
    if token != "dummy_token":
        auth_success = await connector.authenticate()
        print(f"   -> Authentication success: {auth_success}")
        if not auth_success:
            print("   -> Failed to authenticate. Is the token valid?")
            return
    else:
        print("   -> Using dummy token. Skipping /user authentication check.")
        
    print(f"\n2. Running partial sync against {repo}...")
    
    try:
        count = 0
        async for raw_doc in connector.sync():
            doc = await connector.normalize(raw_doc)
            print(f"   -> Yielded: [{doc['source']}] {doc['title']} ({len(doc['content'])} bytes)")
            count += 1
            if count >= 5: # Just fetch 5 items to prove it works
                print("   -> Reached 5 items. Stopping partial sync.")
                break
                
        print("\nSUCCESS: GitHub Connector successfully fetched and normalized data!")
        
    except Exception as e:
        print(f"\nFAILED: {e}")
        print("Note: If this is a 401 or 403, it's because GitHub requires a valid token or you hit the rate limit. Export GITHUB_TOKEN to test.")

if __name__ == "__main__":
    asyncio.run(verify_github_connector())
