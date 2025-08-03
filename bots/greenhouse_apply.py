import asyncio
import uuid
from playwright.async_api import async_playwright
import argparse

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()

    if args.demo:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto("file:///home/tom/nl-autopilot/sandbox/demo_greenhouse_posting.html")
            await page.fill("input[name='first_name']", "Test")
            await page.fill("input[name='last_name']", "User")
            await page.fill("input[name='email']", "test@example.com")
            await page.fill("input[name='phone']", "1234567890")
            await page.locator("input[type='submit']").click()
            await browser.close()
        print(f"CONFIRM_ID={uuid.uuid4()}")

if __name__ == "__main__":
    asyncio.run(main())