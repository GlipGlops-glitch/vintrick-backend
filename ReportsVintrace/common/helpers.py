"""
ReportsVintrace Common Helper Functions
Refactored helper functions using the new Selectors system

Author: GlipGlops-glitch
Created: 2025-01-19
Refactored from: tools/vintrace_helpers.py
"""

import asyncio
import os
import time
import datetime
from typing import Optional
from playwright.async_api import Page, Frame

from Selectors.old_ui.common import IframeSelectors, LoaderSelectors
from Selectors.old_ui.navigation import NavigationSelectors
from Selectors.old_ui.reports import ReportsSelectors
from Selectors.tracking import track_selector_attempt
from ReportsVintrace.config import (
    LARGE_TIMEOUT,
    MEDIUM_TIMEOUT,
    STANDARD_TIMEOUT,
    SHORT_TIMEOUT,
    DEBUG_SCREENSHOT_DIR,
)


async def wait_for_all_vintrace_loaders(page_or_frame, timeout=LARGE_TIMEOUT):
    """
    Wait for all Vintrace loading indicators to disappear.
    Works with both Page and Frame objects.
    
    Args:
        page_or_frame: Playwright Page or Frame object
        timeout: Maximum wait time in milliseconds
    """
    try:
        print("⏳ Waiting for Vintrace loaders to disappear...")
        await page_or_frame.wait_for_function(
            """
            () => {
                // Function to check if loader is hidden in a document
                function allLoadersHidden(doc) {
                    // Check for loader in iframe with specific ID pattern (new UI)
                    const loaderDivs = doc.querySelectorAll('[id^="loader_Iframe_"]');
                    for (let loader of loaderDivs) {
                        const style = window.getComputedStyle(loader);
                        // If any loader is visible, return false
                        if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                            return false;
                        }
                    }

                    // Check for the old-style loaders (classic vintrace)
                    const long = doc.getElementById('serverDelayMessageLong');
                    const main = doc.getElementById('serverDelayMessage');
                    const longHidden = !long || getComputedStyle(long).visibility === 'hidden';
                    const mainHidden = !main || getComputedStyle(main).visibility === 'hidden';

                    return longHidden && mainHidden;
                }

                return allLoadersHidden(document);
            }
            """,
            timeout=timeout
        )
        print("✓ All Vintrace loaders hidden")
    except Exception as e:
        print(f"⚠ Timeout waiting for loaders to hide (may be okay): {e}")


async def get_main_iframe(page: Page):
    """
    Get the main iframe that contains the Vintrace application.
    Uses selectors from Selectors.old_ui.common.IframeSelectors with performance tracking.
    
    Args:
        page: Playwright Page object
    
    Returns:
        Frame or Page: The iframe if found, otherwise the page itself
    """
    print("🔍 Looking for main Vintrace iframe...")
    
    await asyncio.sleep(2)
    
    # Use selectors from the Selectors system
    iframe_selectors = IframeSelectors.IFRAME_MAIN.copy()
    
    # Add fallback selectors
    iframe_selectors.extend([
        "iframe[src*='xhtml']",  # Source contains xhtml
        "iframe[name*='vintrace' i]",
        "iframe[src*='vintrace']",
        "iframe"  # Final fallback
    ])
    
    for selector in iframe_selectors:
        start_time = time.time()
        try:
            iframe_element = await page.wait_for_selector(selector, timeout=MEDIUM_TIMEOUT, state="attached")
            if iframe_element:
                iframe = await iframe_element.content_frame()
                if iframe:
                    time_ms = (time.time() - start_time) * 1000
                    print(f"✓ Found iframe using selector: {selector}")
                    # Track successful selector
                    track_selector_attempt(
                        category="iframe_main",
                        selector=selector,
                        success=True,
                        time_ms=time_ms,
                        context="old_ui_main_iframe"
                    )
                    # Wait for iframe to load
                    await iframe.wait_for_load_state("domcontentloaded", timeout=STANDARD_TIMEOUT)
                    return iframe
        except Exception as e:
            time_ms = (time.time() - start_time) * 1000
            track_selector_attempt(
                category="iframe_main",
                selector=selector,
                success=False,
                time_ms=time_ms,
                context="old_ui_main_iframe"
            )
            print(f"  ✗ Failed to find iframe with selector '{selector}': {e}")
            continue
    
    print("⚠ No iframe found, using main page")
    return page


async def navigate_to_reports_old_ui(page_or_frame):
    """
    Navigate to Reports section in old Vintrace UI.
    Uses selectors from Selectors.old_ui.navigation.NavigationSelectors.
    
    Args:
        page_or_frame: Playwright Page or Frame object (the main Vintrace iframe or page)
    
    Returns:
        bool: True if navigation successful, False otherwise
    """
    print("\n🔍 Navigating to Reports section...")
    
    # Use selectors from the Selectors system
    reports_icon_selectors = NavigationSelectors.REPORTS_ICON.copy()
    
    for selector in reports_icon_selectors:
        start_time = time.time()
        try:
            element = await page_or_frame.query_selector(selector)
            if element:
                is_visible = await element.is_visible()
                if is_visible:
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await element.click()
                    time_ms = (time.time() - start_time) * 1000
                    print(f"  ✓ Clicked Reports icon using selector: {selector}")
                    track_selector_attempt(
                        category="reports_icon",
                        selector=selector,
                        success=True,
                        time_ms=time_ms,
                        context="old_ui_reports"
                    )
                    await wait_for_all_vintrace_loaders(page_or_frame)
                    await asyncio.sleep(2)
                    print("✓ Successfully navigated to Reports section")
                    return True
        except Exception as e:
            time_ms = (time.time() - start_time) * 1000
            track_selector_attempt(
                category="reports_icon",
                selector=selector,
                success=False,
                time_ms=time_ms,
                context="old_ui_reports"
            )
            print(f"  ✗ Failed with selector '{selector}': {e}")
            continue
    
    print("❌ Could not navigate to Reports section")
    return False


async def find_report_strip_by_title(page_or_frame, report_title: str):
    """
    Find a specific report strip section by its title.
    Uses selectors from Selectors.old_ui.reports.ReportsSelectors.
    
    Args:
        page_or_frame: Playwright Page or Frame object
        report_title: Title of the report (e.g., "Analysis data export")
    
    Returns:
        ElementHandle or None: The reportStrip div if found, None otherwise
    """
    print(f"\n🔍 Looking for report strip: '{report_title}'")
    
    start_time = time.time()
    selector = ReportsSelectors.REPORT_STRIP
    
    try:
        # Wait for report strips to load
        await page_or_frame.wait_for_selector(selector, timeout=MEDIUM_TIMEOUT)
        
        # Find all report strips
        report_strips = await page_or_frame.query_selector_all(selector)
        
        for strip in report_strips:
            # Get all text content in this strip
            text_content = await strip.inner_text()
            
            # Check if the title is in this strip
            if report_title in text_content:
                time_ms = (time.time() - start_time) * 1000
                print(f"✓ Found report strip for '{report_title}'")
                track_selector_attempt(
                    category="report_strip",
                    selector=selector,
                    success=True,
                    time_ms=time_ms,
                    context=f"old_ui_reports_{report_title.replace(' ', '_')}"
                )
                return strip
        
        time_ms = (time.time() - start_time) * 1000
        print(f"❌ Could not find report strip for '{report_title}'")
        track_selector_attempt(
            category="report_strip",
            selector=selector,
            success=False,
            time_ms=time_ms,
            context=f"old_ui_reports_{report_title.replace(' ', '_')}"
        )
        return None
    
    except Exception as e:
        time_ms = (time.time() - start_time) * 1000
        print(f"❌ Error finding report strip: {e}")
        track_selector_attempt(
            category="report_strip",
            selector=selector,
            success=False,
            time_ms=time_ms,
            context=f"old_ui_reports_{report_title.replace(' ', '_')}"
        )
        return None


async def save_debug_screenshot(page: Page, name: str):
    """
    Save a debug screenshot with a timestamp.
    
    Args:
        page: Playwright Page object
        name: Base name for the screenshot file
    
    Returns:
        str: Path to the saved screenshot
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debug_{name}_{timestamp}.png"
    
    # Create screenshots directory if it doesn't exist
    os.makedirs(DEBUG_SCREENSHOT_DIR, exist_ok=True)
    
    filepath = os.path.join(DEBUG_SCREENSHOT_DIR, filename)
    
    try:
        await page.screenshot(path=filepath, full_page=True)
        print(f"📸 Debug screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"⚠ Could not save screenshot: {e}")
        return None
