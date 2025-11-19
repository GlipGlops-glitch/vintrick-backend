"""
Base Report Class for Vintrace Reports
Abstract base class that all report downloaders should inherit from

Author: GlipGlops-glitch
Created: 2025-01-19

This base class provides:
- Standardized initialization
- Browser management
- Login workflow
- Download directory setup
- Cleanup methods
"""

import os
import asyncio
from abc import ABC, abstractmethod
from typing import Optional
from playwright.async_api import async_playwright

from ReportsVintrace.common.helpers import (
    load_vintrace_credentials,
    initialize_browser,
    vintrace_login,
    save_debug_screenshot,
    wait_for_all_vintrace_loaders,
    get_main_iframe,
)
from ReportsVintrace.config import DEFAULT_HEADLESS, DEFAULT_DOWNLOAD_DIRS
from Selectors.tracking import track_selector_attempt


class VintraceReport(ABC):
    """
    Base class for all Vintrace report downloaders.
    
    All report classes should inherit from this and implement the download() method.
    
    Example:
        >>> class VesselsReport(VintraceReport):
        ...     async def download(self, output_filename="vessels.csv"):
        ...         # Implementation here
        ...         pass
    """

    def __init__(
        self,
        headless: bool = DEFAULT_HEADLESS,
        download_dir: Optional[str] = None,
        report_type: str = "general"
    ):
        """
        Initialize the report downloader.

        Args:
            headless: Run browser in headless mode
            download_dir: Custom download directory (uses default if None)
            report_type: Type of report (vessels, barrels, analysis, fruit)
        """
        self.headless = headless
        self.report_type = report_type
        
        # Set download directory
        if download_dir:
            self.download_dir = download_dir
        elif report_type in DEFAULT_DOWNLOAD_DIRS:
            self.download_dir = DEFAULT_DOWNLOAD_DIRS[report_type]
        else:
            self.download_dir = f"Main/data/vintrace_reports/{report_type}/"
        
        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)

        # Browser components (initialized in __aenter__)
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.iframe = None
        
        # Credentials
        self.username = None
        self.password = None

    async def __aenter__(self):
        """Context manager entry - initialize browser."""
        await self.init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup browser."""
        await self.cleanup()

    async def init_browser(self):
        """Initialize the browser and page."""
        print(f"\n{'=' * 60}")
        print(f"INITIALIZING {self.__class__.__name__}")
        print(f"{'=' * 60}")
        
        self.playwright, self.browser, self.context, self.page = await initialize_browser(
            headless=self.headless,
            download_dir=self.download_dir
        )

    async def login(self, username: Optional[str] = None, password: Optional[str] = None, use_old_ui: bool = False):
        """
        Login to Vintrace using standard workflow.

        Args:
            username: Vintrace username (loads from env if None)
            password: Vintrace password (loads from env if None)
            use_old_ui: Navigate to old UI after login

        Returns:
            bool: True if login successful
        """
        # Load credentials if not provided
        if not username or not password:
            username, password = load_vintrace_credentials()
            if not username or not password:
                print("❌ ERROR: No credentials available")
                return False

        self.username = username
        self.password = password

        # Perform login
        success = await vintrace_login(self.page, username, password, use_old_ui=use_old_ui)
        
        if success:
            # Get main iframe after login
            self.iframe = await get_main_iframe(self.page)
            
        return success

    @abstractmethod
    async def download(self, **kwargs):
        """
        Download the report. Must be implemented by subclasses.

        Args:
            **kwargs: Report-specific parameters

        Returns:
            bool or str: True/filename if successful, False otherwise
        """
        pass

    async def wait_for_loaders(self):
        """Wait for all page loaders to complete."""
        target = self.iframe if self.iframe else self.page
        await wait_for_all_vintrace_loaders(target)

    async def screenshot(self, name: str = "debug"):
        """Take a debug screenshot."""
        if self.page:
            return await save_debug_screenshot(self.page, name)
        return None

    def track_success(
        self,
        selector_category: str,
        selector: str,
        success: bool,
        time_ms: Optional[float] = None,
        context: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """
        Track a selector attempt for learning.

        Args:
            selector_category: Category of selector (e.g., 'export_button')
            selector: The actual selector string
            success: Whether it worked
            time_ms: Time taken in milliseconds
            context: Additional context
            notes: Additional notes
        """
        track_selector_attempt(
            category=selector_category,
            selector=selector,
            success=success,
            time_ms=time_ms,
            context=context or self.report_type,
            notes=notes
        )

    async def cleanup(self):
        """Close browser and cleanup resources."""
        print(f"\n{'=' * 60}")
        print("CLEANUP")
        print(f"{'=' * 60}")

        if self.context:
            await self.context.close()
            print("✓ Browser context closed")

        if self.browser:
            await self.browser.close()
            print("✓ Browser closed")

        if self.playwright:
            await self.playwright.stop()
            print("✓ Playwright stopped")

        print(f"✓ {self.__class__.__name__} cleanup complete")


class NewUIReport(VintraceReport):
    """
    Base class for reports using the new/current UI.
    Automatically sets use_old_ui=False for login.
    """

    async def login(self, username: Optional[str] = None, password: Optional[str] = None, use_old_ui: bool = False):
        """Login using new UI (overrides default)."""
        return await super().login(username, password, use_old_ui=False)


class OldUIReport(VintraceReport):
    """
    Base class for reports using the old/legacy UI.
    Automatically sets use_old_ui=True for login.
    """

    async def login(self, username: Optional[str] = None, password: Optional[str] = None, use_old_ui: bool = True):
        """Login using old UI (overrides default)."""
        return await super().login(username, password, use_old_ui=True)
