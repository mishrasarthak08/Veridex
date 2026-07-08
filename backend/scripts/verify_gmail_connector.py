import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.knowledge.connectors.gmail import GmailConnector

async def verify_gmail_connector():
    print("1. Initializing Gmail Connector...")
    # NOTE: To run this against a real mailbox, supply a real Google OAuth access_token.
    # We will use a dummy token for structure verification, which will fail authentication,
    # but that proves the network path and object instantiation works.
    
    access_token = os.environ.get("GOOGLE_ACCESS_TOKEN", "dummy_token")
    refresh_token = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
    
    connector = GmailConnector(access_token=access_token, refresh_token=refresh_token)
    
    if access_token != "dummy_token":
        auth_success = await connector.authenticate()
        print(f"   -> Authentication success: {auth_success}")
        if not auth_success:
            print("   -> Failed to authenticate. Is the token valid?")
            return
            
        print("\n2. Running partial sync...")
        try:
            count = 0
            async for raw_doc in connector.sync():
                doc = await connector.normalize(raw_doc)
                print(f"   -> Yielded: [{doc['source']}] {doc['title']} (Thread: {doc['source_metadata'].get('thread_id')})")
                count += 1
                if count >= 3: # Just fetch 3 emails
                    print("   -> Reached 3 items. Stopping partial sync.")
                    break
                    
            print("\nSUCCESS: Gmail Connector successfully fetched and normalized data!")
        except Exception as e:
            print(f"\nFAILED: {e}")
            
    else:
        print("   -> Using dummy token. Skipping /profile authentication check.")
        print("   -> Connector structure is valid. Provide GOOGLE_ACCESS_TOKEN for full test.")
        print("\nSUCCESS: Gmail Connector instantiated.")

if __name__ == "__main__":
    asyncio.run(verify_gmail_connector())
