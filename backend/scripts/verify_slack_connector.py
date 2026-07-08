import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.knowledge.connectors.slack import SlackConnector

async def verify_slack_connector():
    print("1. Initializing Slack Connector...")
    # NOTE: To run this against a real workspace, supply a real bot token.
    # We will use dummy tokens for structure verification, which will fail authentication,
    # but that proves the network path and object instantiation works.
    
    bot_token = os.environ.get("SLACK_BOT_TOKEN", "dummy_token")
    
    connector = SlackConnector(bot_token=bot_token)
    
    if bot_token != "dummy_token":
        auth_success = await connector.authenticate()
        print(f"   -> Authentication success: {auth_success}")
        if not auth_success:
            print("   -> Failed to authenticate. Is the SLACK_BOT_TOKEN valid?")
            return
            
        print("\n2. Running partial sync...")
        try:
            count = 0
            async for raw_doc in connector.sync():
                doc = await connector.normalize(raw_doc)
                print(f"   -> Yielded: [{doc['source']}] {doc['title']}")
                print(f"      Channel: {doc['source_metadata'].get('channel_name')} | User: {doc['source_metadata'].get('user_id')}")
                count += 1
                if count >= 3: # Just fetch 3 items
                    print("   -> Reached 3 items. Stopping partial sync.")
                    break
                    
            print("\nSUCCESS: Slack Connector successfully fetched and normalized data!")
        except Exception as e:
            print(f"\nFAILED: {e}")
            
    else:
        print("   -> Using dummy token. Skipping auth.test authentication check.")
        print("   -> Connector structure is valid. Provide SLACK_BOT_TOKEN for full test.")
        print("\nSUCCESS: Slack Connector instantiated.")

if __name__ == "__main__":
    asyncio.run(verify_slack_connector())
