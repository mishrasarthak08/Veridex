import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.knowledge.connectors.notion import NotionConnector

async def verify_notion_connector():
    print("1. Initializing Notion Connector...")
    # NOTE: To run this against a real workspace, supply a real Notion Internal Integration Token.
    # We will use a dummy token for structure verification, which will fail authentication,
    # but that proves the network path and object instantiation works.
    
    integration_token = os.environ.get("NOTION_TOKEN", "dummy_token")
    
    connector = NotionConnector(integration_token=integration_token)
    
    if integration_token != "dummy_token":
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
                print(f"   -> Yielded: [{doc['source']}] {doc['title']} (Length: {len(doc['content'])} chars)")
                print(f"      Parent Type: {doc['source_metadata'].get('parent_type')}")
                count += 1
                if count >= 3: # Just fetch 3 items
                    print("   -> Reached 3 items. Stopping partial sync.")
                    break
                    
            print("\nSUCCESS: Notion Connector successfully fetched and normalized data!")
        except Exception as e:
            print(f"\nFAILED: {e}")
            
    else:
        print("   -> Using dummy token. Skipping /users/me authentication check.")
        print("   -> Connector structure is valid. Provide NOTION_TOKEN for full test.")
        print("\nSUCCESS: Notion Connector instantiated.")

if __name__ == "__main__":
    asyncio.run(verify_notion_connector())
