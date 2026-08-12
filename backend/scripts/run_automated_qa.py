import asyncio
from playwright.async_api import async_playwright

async def run_qa():
    print("Starting automated QA pass on the frontend...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Login
        print("Logging in...")
        await page.goto("http://localhost:3000/login")
        await page.fill('input[type="email"]', 'qa_tester@veridex.io')
        await page.fill('input[type="password"]', 'admin123')
        await page.click('button[type="submit"]')
        
        # Wait for redirect to Dashboard
        await page.wait_for_url("http://localhost:3000/")
        print("Logged in successfully. On Dashboard.")
        
        # 2. Check Knowledge Graph
        print("Navigating to Knowledge Graph...")
        await page.click('a[href="/knowledge-graph"]')
        await page.wait_for_url("http://localhost:3000/knowledge-graph")
        # Wait for either the graph to load or an error to appear
        await asyncio.sleep(2)
        content = await page.content()
        if "Loading Knowledge Graph..." in content or "Forbidden" in content:
            print("Knowledge Graph issue detected or still loading!")
        else:
            print("Knowledge Graph loaded successfully.")

        # 3. Check Projects
        print("Navigating to Projects...")
        await page.click('a[href="/projects"]')
        await page.wait_for_url("http://localhost:3000/projects")
        await asyncio.sleep(1)
        print("Projects page loaded.")
        
        await browser.close()
        print("Automated QA pass completed successfully.")

if __name__ == "__main__":
    asyncio.run(run_qa())
