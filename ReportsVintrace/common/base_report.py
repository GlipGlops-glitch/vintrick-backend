"""
ReportsVintrace Base Report Classes
Base classes for Vintrace report automation

Author: GlipGlops-glitch
Created: 2025-01-19
"""

import asyncio
import os
from typing import Optional
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from dotenv import load_dotenv

from ReportsVintrace.config import OLD_URL, LOGIN_URL


class BaseReport(ABC):
    """
    Abstract base class for all Vintrace reports.
    Provides common functionality for browser management and login.
    """
    
    def __init__(self, headless: bool = False, download_dir: Optional[str] = None):
        """
        Initialize the base report.
        
        Args:
            headless: Whether to run browser in headless mode
            download_dir: Directory for downloads (default: subclass specific)
        """
        self.headless = headless
        self.download_dir = download_dir
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def __aenter__(self):
        """Context manager entry - initialize browser"""
        await self.initialize_browser()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup browser"""
        await self.close()
        
    async def initialize_browser(self):
        """Initialize Playwright browser and context"""
        print("🌐 Initializing browser...")
        self.playwright = await async_playwright().start()
        
        # Launch browser
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--start-maximized']
        )
        
        # Create context with download directory if specified
        context_options = {
            'viewport': None,
            'no_viewport': True,
        }
        
        if self.download_dir:
            os.makedirs(self.download_dir, exist_ok=True)
            context_options['accept_downloads'] = True
        
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        print("✓ Browser initialized")
        
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            print("🔒 Closing browser...")
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    def load_credentials(self):
        """
        Load Vintrace credentials from environment variables.
        
        Returns:
            tuple: (username, password) or raises exception if not found
        """
        load_dotenv()
        username = os.getenv("VINTRACE_USER")
        password = os.getenv("VINTRACE_PW")
        
        if not username or not password:
            raise ValueError("VINTRACE_USER or VINTRACE_PW environment variables not set")
        
        return username, password
    
    @abstractmethod
    async def login(self):
        """Login to Vintrace - must be implemented by subclass"""
        pass
        
    @abstractmethod
    async def download(self, **kwargs) -> bool:
        """Download report - must be implemented by subclass"""
        pass


class OldUIReport(BaseReport):
    """
    Base class for reports using the Old Vintrace UI.
    Provides login functionality for old UI.
    """
    
    async def login(self):
        """
        Login to Vintrace and navigate to old UI.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        print("\n" + "=" * 60)
        print("STEP 1: LOGGING IN TO VINTRACE (OLD UI)")
        print("=" * 60)
        
        # Load credentials
        try:
            username, password = self.load_credentials()
        except ValueError as e:
            print(f"❌ {e}")
            return False
        
        print(f"📧 Using credentials for: {username}")
        
        # Navigate to login page
        print(f"🌐 Navigating to login page...")
        await self.page.goto(LOGIN_URL, wait_until="domcontentloaded")
        
        # Fill in login form
        try:
            print("🔑 Filling in login credentials...")
            
            # Email field
            email_input = await self.page.wait_for_selector("input[type='email'], input[name='email'], input#email", timeout=10000)
            await email_input.fill(username)
            print("  ✓ Email entered")
            
            # Password field
            password_input = await self.page.wait_for_selector("input[type='password'], input[name='password'], input#password", timeout=10000)
            await password_input.fill(password)
            print("  ✓ Password entered")
            
            # Submit button
            submit_button = await self.page.wait_for_selector("button[type='submit'], button:has-text('Sign in'), button:has-text('Login')", timeout=10000)
            await submit_button.click()
            print("  ✓ Clicked login button")
            
        except Exception as e:
            print(f"❌ Error during login: {e}")
            return False
        
        # Wait for navigation and then go to old UI
        print("⏳ Waiting for authentication...")
        await asyncio.sleep(3)
        
        # Navigate to old Vintrace URL
        print(f"🔄 Navigating to Old Vintrace UI...")
        await self.page.goto(OLD_URL, wait_until="domcontentloaded")
        await asyncio.sleep(3)
        
        # Verify we're on the old UI
        current_url = self.page.url
        if "oldVintrace=true" in current_url:
            print("✓ Successfully logged in to Old Vintrace UI")
            print("=" * 60)
            return True
        else:
            print("⚠ WARNING: May not be on old Vintrace UI")
            print(f"Current URL: {current_url}")
            print("=" * 60)
            return True  # Continue anyway
