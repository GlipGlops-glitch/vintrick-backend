#python tools/login_and_pause.py

"""
Test script to login to Vintrace and pause for HTML inspection
Usage: python test_login_and_pause.py
"""

import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Login credentials
LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"

async def login_and_pause():
    """Login to Vintrace and pause for inspection"""
    
    # Load credentials
    load_dotenv()
    USERNAME = os.getenv("VINTRACE_USER")
    PASSWORD = os.getenv("VINTRACE_PW")
    
    if not USERNAME or not PASSWORD:
        print("❌ ERROR: VINTRACE_USER or VINTRACE_PW environment variables not set.")
        return
    
    print("=" * 60)
    print("VINTRACE LOGIN TEST & HTML INSPECTOR")
    print("=" * 60)
    
    async with async_playwright() as p:
        # Launch browser in non-headless mode so you can see it
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to login page
        print(f"\n📍 Navigating to: {LOGIN_URL}")
        await page.goto(LOGIN_URL, timeout=1200000)
        await page.wait_for_load_state("networkidle")
        print("✓ Login page loaded")
        
        # Fill in credentials
        print(f"\n🔐 Logging in as: {USERNAME}")
        
        # Fill email
        try:
            await page.wait_for_selector("input#email", timeout=100000)
            await page.fill("input#email", USERNAME)
            print("✓ Email filled")
        except Exception as e:
            print(f"❌ Could not fill email: {e}")
            await browser.close()
            return
        
        await asyncio.sleep(0.3)
        
        # Fill password
        try:
            await page.wait_for_selector("input#password", timeout=100000)
            await page.fill("input#password", PASSWORD)
            print("✓ Password filled")
        except Exception as e:
            print(f"❌ Could not fill password: {e}")
            await browser.close()
            return
        
        await asyncio.sleep(0.3)
        
        # Click login button
        try:
            login_btn = await page.wait_for_selector("button[type='submit']:has-text('Login')", timeout=100000)
            await login_btn.click()
            print("✓ Login button clicked")
        except Exception as e:
            print(f"❌ Could not click login button: {e}")
            await browser.close()
            return
        
        # Wait for navigation
        print("\n⏳ Waiting for login to complete...")
        try:
            await page.wait_for_url(lambda url: url != LOGIN_URL and "/sign-in" not in url, timeout=600000)
            print(f"✓ Successfully logged in!")
            print(f"  Current URL: {page.url}")
        except Exception as e:
            print(f"❌ Login may have failed: {e}")
            print(f"  Current URL: {page.url}")
        
        # Wait for page to fully load
        await page.wait_for_load_state("networkidle", timeout=600000)
        await asyncio.sleep(3)  # Extra time for any dynamic content
        
        # Print the current page HTML to console
        print("\n" + "=" * 60)
        print("PAGE HTML (First 2000 characters)")
        print("=" * 60)
        html_content = await page.content()
        print(html_content[:2000])
        print("\n... (truncated, see full HTML in browser DevTools)")
        print("=" * 60)
        
        # Save full HTML to file
        html_filename = "vintrace_homepage.html"
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n✓ Full HTML saved to: {html_filename}")
        
        # Instructions for user
        print("\n" + "=" * 60)
        print("🔍 INSPECTION MODE - BROWSER PAUSED")
        print("=" * 60)
        print("\nThe browser window is now open and logged in.")
        print("\nTo get the exact HTML:")
        print("  1. Open DevTools in the browser (F12 or Right-click > Inspect)")
        print("  2. Go to the 'Elements' or 'Inspector' tab")
        print("  3. Right-click on the <html> tag at the top")
        print("  4. Select 'Copy' > 'Copy outerHTML'")
        print("  5. Paste it wherever you need it")
        print(f"\nAlternatively, the HTML has been saved to: {html_filename}")
        print("\nCurrent page URL:", page.url)
        print("\nPress Enter in this terminal when you're done inspecting...")
        print("=" * 60)
        
        # Wait for user input before closing
        input()
        
        print("\n✓ Closing browser...")
        await browser.close()
        print("✓ Done!")

if __name__ == "__main__":
    asyncio.run(login_and_pause())