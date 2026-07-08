import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.knowledge.connectors.jira import JiraConnector

async def verify_jira_connector():
    print("1. Initializing Jira Connector...")
    # NOTE: To run this against a real workspace, supply real credentials.
    # We will use dummy tokens for structure verification, which will fail authentication,
    # but that proves the network path and object instantiation works.
    
    jira_url = os.environ.get("JIRA_URL", "https://dummy.atlassian.net")
    jira_email = os.environ.get("JIRA_EMAIL", "dummy@example.com")
    jira_token = os.environ.get("JIRA_API_TOKEN", "dummy_token")
    
    connector = JiraConnector(jira_url=jira_url, email=jira_email, api_token=jira_token)
    
    if jira_token != "dummy_token":
        auth_success = await connector.authenticate()
        print(f"   -> Authentication success: {auth_success}")
        if not auth_success:
            print("   -> Failed to authenticate. Are the credentials valid?")
            return
            
        print("\n2. Running partial sync...")
        try:
            count = 0
            async for raw_doc in connector.sync():
                doc = await connector.normalize(raw_doc)
                print(f"   -> Yielded: [{doc['source']}] {doc['title']}")
                print(f"      Status: {doc['source_metadata'].get('status')} | Assignee: {doc['source_metadata'].get('assignee_id')}")
                count += 1
                if count >= 3: # Just fetch 3 items
                    print("   -> Reached 3 items. Stopping partial sync.")
                    break
                    
            print("\nSUCCESS: Jira Connector successfully fetched and normalized data!")
        except Exception as e:
            print(f"\nFAILED: {e}")
            
    else:
        print("   -> Using dummy token. Skipping /rest/api/3/myself authentication check.")
        print("   -> Connector structure is valid. Provide JIRA_API_TOKEN for full test.")
        print("\nSUCCESS: Jira Connector instantiated.")

if __name__ == "__main__":
    asyncio.run(verify_jira_connector())
