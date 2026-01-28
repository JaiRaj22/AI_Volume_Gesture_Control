import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # Navigate to the local file
        import os
        path = os.path.abspath("ddos_dashboard/frontend/index.html")
        await page.goto(f"file://{path}")
        # Wait for some content to load (globe takes a second)
        await asyncio.sleep(5)
        # Take a screenshot
        await page.screenshot(path="final_frontend_check.png")
        print("Screenshot saved as final_frontend_check.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
