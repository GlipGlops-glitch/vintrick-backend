"""
Common Helper Functions for Vintrace Reports
Refactored helper functions using the new Selectors system

Author: GlipGlops-glitch
Created: 2025-01-19

This module provides reusable functions for:
- Browser initialization
- Login workflows
- Loader waiting
- Iframe navigation
- Debug/screenshot utilities
"""

import asyncio
import os
import datetime
from typing import Optional, Tuple
from playwright.async_api import Page, Frame, async_playwright
from dotenv import load_dotenv

# Import new Selectors system
from Selectors.common import LoginSelectors, PopupSelectors
from Selectors.new_ui.common import IframeSelectors, LoaderSelectors as NewUILoaderSelectors
from Selectors.old_ui.common import LoaderSelectors as OldUILoaderSelectors
from Selectors.old_ui.navigation import NavigationSelectors as OldUINavigationSelectors
from Selectors.tracking import track_selector_attempt

# Import config
from ReportsVintrace.config import (
    LOGIN_URL, OLD_URL, NEW_URL,
    STANDARD_TIMEOUT, MEDIUM_TIMEOUT, SHORT_TIMEOUT, LARGE_DOWNLOAD_TIMEOUT
)


# ============================================================================
# CREDENTIAL MANAGEMENT
# ============================================================================

def load_vintrace_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Load Vintrace credentials from environment variables.

    Returns:
        tuple: (username, password) or (None, None) if not found
    """
    load_dotenv()
    username = os.getenv("VINTRACE_USER")
    password = os.getenv("VINTRACE_PW")

    if not username or not password:
        print("❌ ERROR: VINTRACE_USER or VINTRACE_PW environment variables not set.")
        print("   Please set them in your .env file.")
        return None, None

    return username, password


# ============================================================================
# BROWSER INITIALIZATION
# ============================================================================

async def initialize_browser(headless: bool = False, download_dir: Optional[str] = None):
    """
    Initialize Playwright browser with standard settings.

    Args:
        headless: Whether to run in headless mode
        download_dir: Directory for downloads (optional)

    Returns:
        tuple: (playwright, browser, context, page)
    """
    print(f"🌐 Initializing browser (headless={headless})...")

    playwright = await async_playwright().start()
    
    browser_args = ['--disable-blink-features=AutomationControlled']
    browser = await playwright.chromium.launch(
        headless=headless,
        args=browser_args
    )

    # Create context with download settings if specified
    context_options = {
        'viewport': {'width': 1920, 'height': 1080},
    }
    
    if download_dir:
        context_options['accept_downloads'] = True
        # Note: downloads_path is set in the download handler, not here

    context = await browser.new_context(**context_options)
    page = await context.new_page()

    print("✓ Browser initialized")
    return playwright, browser, context, page


# ============================================================================
# LOADER WAITING FUNCTIONS
# ============================================================================

async def wait_for_all_vintrace_loaders(
    page_or_frame,
    timeout: int = LARGE_DOWNLOAD_TIMEOUT
):
    """
    Wait for all Vintrace loading indicators to disappear.
    Works with both Page and Frame objects for both new and old UI.

    Args:
        page_or_frame: Playwright Page or Frame object
        timeout: Maximum wait time in milliseconds
    """
    try:
        print("⏳ Waiting for Vintrace loaders to disappear...")
        await page_or_frame.wait_for_function(
            """
            () => {
                function allLoadersHidden(doc) {
                    // Check for new UI loaders
                    const loaderDivs = doc.querySelectorAll('[id^="loader_Iframe_"]');
                    for (let loader of loaderDivs) {
                        const style = window.getComputedStyle(loader);
                        if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                            return false;
                        }
                    }

                    // Check for old UI loaders
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


async def wait_for_loader_to_appear(
    page_or_frame,
    timeout: int = STANDARD_TIMEOUT
) -> bool:
    """
    Wait for Vintrace loading indicators to APPEAR (become visible).
    Useful to ensure a page action triggered loading before waiting for it to complete.

    Args:
        page_or_frame: Playwright Page or Frame object
        timeout: Maximum wait time in milliseconds

    Returns:
        bool: True if loader appeared, False if not
    """
    try:
        print("⏳ Waiting for Vintrace loader to appear...")
        await page_or_frame.wait_for_function(
            """
            () => {
                function hasVisibleLoader(doc) {
                    // Check for new UI loaders
                    const loaderDivs = doc.querySelectorAll('[id^="loader_Iframe_"]');
                    for (let loader of loaderDivs) {
                        const style = window.getComputedStyle(loader);
                        if (style.display !== 'none' && style.visibility !== 'hidden' && style.opacity !== '0') {
                            return true;
                        }
                    }

                    // Check for old UI loaders
                    const long = doc.getElementById('serverDelayMessageLong');
                    const main = doc.getElementById('serverDelayMessage');
                    const longVisible = long && getComputedStyle(long).visibility !== 'hidden';
                    const mainVisible = main && getComputedStyle(main).visibility !== 'hidden';

                    return longVisible || mainVisible;
                }

                return hasVisibleLoader(document);
            }
            """, timeout=timeout
        )
        print("✓ Vintrace loader appeared")
        return True
    except Exception as e:
        print(f"⚠ Loader never appeared (page might have loaded instantly): {e}")
        return False


# ============================================================================
# IFRAME MANAGEMENT
# ============================================================================

async def get_main_iframe(page: Page):
    """
    Get the main iframe that contains the Vintrace application.
    Uses the new Selectors system with tracking.

    Args:
        page: Playwright Page object

    Returns:
        Frame or Page: The iframe if found, otherwise the page itself
    """
    print("🔍 Looking for main Vintrace iframe...")
    await asyncio.sleep(2)

    iframe_selectors = IframeSelectors.IFRAME_MAIN.copy()
    
    # Add fallback selectors
    iframe_selectors.extend([
        "iframe[src*='xhtml']",
        "iframe[name*='vintrace' i]",
        "iframe[src*='vintrace']",
        "iframe"
    ])

    for selector in iframe_selectors:
        start_time = datetime.datetime.now()
        try:
            iframe_element = await page.wait_for_selector(
                selector,
                timeout=MEDIUM_TIMEOUT,
                state="attached"
            )
            if iframe_element:
                iframe = await iframe_element.content_frame()
                if iframe:
                    elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
                    print(f"✓ Found iframe using selector: {selector}")
                    track_selector_attempt(
                        category="main_iframe",
                        selector=selector,
                        success=True,
                        time_ms=elapsed_ms,
                        context="new_ui",
                        notes="Main application iframe"
                    )
                    await iframe.wait_for_load_state("domcontentloaded", timeout=STANDARD_TIMEOUT)
                    return iframe
        except Exception as e:
            elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
            track_selector_attempt(
                category="main_iframe",
                selector=selector,
                success=False,
                time_ms=elapsed_ms,
                context="new_ui"
            )
            print(f"  ✗ Failed with selector '{selector}': {e}")
            continue

    print("⚠ No iframe found, using main page")
    return page


# ============================================================================
# POPUP MANAGEMENT
# ============================================================================

async def close_popups(page_or_frame):
    """
    Close any tour/popup dialogs that appear after login.
    Uses the new Selectors system with tracking.

    Args:
        page_or_frame: Playwright Page or Frame object
    """
    print("\n🔍 Checking for and closing any popups...")

    popup_close_selectors = PopupSelectors.CLOSE_BUTTONS.copy()
    popups_closed = 0

    for selector in popup_close_selectors:
        try:
            buttons = await page_or_frame.query_selector_all(selector)
            for button in buttons:
                try:
                    is_visible = await button.is_visible()
                    if is_visible:
                        await button.click()
                        popups_closed += 1
                        print(f"  ✓ Closed popup using selector: {selector}")
                        track_selector_attempt(
                            category="popup_close",
                            selector=selector,
                            success=True,
                            context="common",
                            notes="Popup close button"
                        )
                        await asyncio.sleep(0.5)
                except Exception:
                    pass
        except Exception:
            pass

    if popups_closed > 0:
        print(f"✓ Closed {popups_closed} popup(s)")
    else:
        print("  No popups found to close")

    await asyncio.sleep(1)


# ============================================================================
# LOGIN FUNCTIONS
# ============================================================================

async def vintrace_login(
    page: Page,
    username: str,
    password: str,
    use_old_ui: bool = False
) -> bool:
    """
    Login to Vintrace application using the new Selectors system.

    Args:
        page: Playwright Page object
        username: Vintrace username/email
        password: Vintrace password
        use_old_ui: Whether to navigate to old UI after login

    Returns:
        bool: True if login successful, False otherwise
    """
    print("=" * 60)
    print("LOGGING IN TO VINTRACE")
    print("=" * 60)
    print(f"Navigating to login page: {LOGIN_URL}")

    await page.goto(LOGIN_URL, timeout=LARGE_DOWNLOAD_TIMEOUT)
    await page.wait_for_load_state("networkidle", timeout=STANDARD_TIMEOUT)
    print("✓ Login page loaded")

    # Ensure Login tab is active
    try:
        await page.wait_for_selector(
            LoginSelectors.LOGIN_TAB[0],
            timeout=SHORT_TIMEOUT
        )
        print("✓ Login tab is active")
    except Exception:
        try:
            login_tab = await page.wait_for_selector(
                LoginSelectors.LOGIN_TAB[1],
                timeout=SHORT_TIMEOUT
            )
            await login_tab.click()
            print("✓ Clicked Login tab")
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"⚠ Could not ensure Login tab is active: {e}")

    # Fill email field
    email_filled = False
    for selector in LoginSelectors.EMAIL_INPUT:
        start_time = datetime.datetime.now()
        try:
            email_input = await page.wait_for_selector(selector, timeout=SHORT_TIMEOUT)
            await email_input.fill(username)
            elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
            print(f"✓ Entered email using selector: {selector}")
            track_selector_attempt(
                category="login_email",
                selector=selector,
                success=True,
                time_ms=elapsed_ms,
                context="login_page"
            )
            email_filled = True
            break
        except Exception as e:
            elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
            track_selector_attempt(
                category="login_email",
                selector=selector,
                success=False,
                time_ms=elapsed_ms,
                context="login_page"
            )
            continue

    if not email_filled:
        print("❌ ERROR: Could not fill email field")
        return False

    # Fill password field
    password_filled = False
    for selector in LoginSelectors.PASSWORD_INPUT:
        start_time = datetime.datetime.now()
        try:
            password_input = await page.wait_for_selector(selector, timeout=SHORT_TIMEOUT)
            await password_input.fill(password)
            elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
            print(f"✓ Entered password using selector: {selector}")
            track_selector_attempt(
                category="login_password",
                selector=selector,
                success=True,
                time_ms=elapsed_ms,
                context="login_page"
            )
            password_filled = True
            break
        except Exception as e:
            elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
            track_selector_attempt(
                category="login_password",
                selector=selector,
                success=False,
                time_ms=elapsed_ms,
                context="login_page"
            )
            continue

    if not password_filled:
        print("❌ ERROR: Could not fill password field")
        return False

    # Click login button
    login_clicked = False
    for selector in LoginSelectors.LOGIN_BUTTON:
        start_time = datetime.datetime.now()
        try:
            login_button = await page.wait_for_selector(selector, timeout=SHORT_TIMEOUT)
            await login_button.click()
            elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
            print(f"✓ Clicked login button using selector: {selector}")
            track_selector_attempt(
                category="login_button",
                selector=selector,
                success=True,
                time_ms=elapsed_ms,
                context="login_page"
            )
            login_clicked = True
            break
        except Exception as e:
            elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
            track_selector_attempt(
                category="login_button",
                selector=selector,
                success=False,
                time_ms=elapsed_ms,
                context="login_page"
            )
            continue

    if not login_clicked:
        print("❌ ERROR: Could not click login button")
        return False

    # Wait for navigation after login
    print("⏳ Waiting for login to complete...")
    await page.wait_for_load_state("networkidle", timeout=STANDARD_TIMEOUT)
    await asyncio.sleep(3)

    # Navigate to appropriate URL
    target_url = OLD_URL if use_old_ui else NEW_URL
    print(f"🔗 Navigating to: {target_url}")
    await page.goto(target_url, timeout=LARGE_DOWNLOAD_TIMEOUT)
    await page.wait_for_load_state("networkidle", timeout=STANDARD_TIMEOUT)
    print("✓ Page loaded after login")

    # Close any popups
    await close_popups(page)

    print("✓ Login successful")
    return True


# ============================================================================
# OLD UI NAVIGATION
# ============================================================================

async def navigate_to_reports_old_ui(iframe) -> bool:
    """
    Navigate to Reports section in the old UI.
    Uses the new Selectors system with tracking.

    Args:
        iframe: Playwright Frame object

    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🔍 Navigating to Reports section (Old UI)...")

    reports_icon_selectors = OldUINavigationSelectors.REPORTS_ICON.copy()

    for selector in reports_icon_selectors:
        start_time = datetime.datetime.now()
        try:
            await iframe.wait_for_selector(selector, timeout=STANDARD_TIMEOUT, state="visible")
            reports_icon = await iframe.query_selector(selector)

            if reports_icon:
                await reports_icon.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
                await reports_icon.click()
                elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
                print(f"✓ Clicked Reports icon using selector: {selector}")
                track_selector_attempt(
                    category="reports_icon_old_ui",
                    selector=selector,
                    success=True,
                    time_ms=elapsed_ms,
                    context="old_ui"
                )
                await wait_for_all_vintrace_loaders(iframe)
                await asyncio.sleep(2)
                return True
        except Exception as e:
            elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
            track_selector_attempt(
                category="reports_icon_old_ui",
                selector=selector,
                success=False,
                time_ms=elapsed_ms,
                context="old_ui"
            )
            print(f"  ✗ Failed with selector '{selector}': {e}")
            continue

    print("❌ ERROR: Could not navigate to Reports section")
    return False


# ============================================================================
# DEBUG/SCREENSHOT UTILITIES
# ============================================================================

async def save_debug_screenshot(page: Page, name: str = "debug"):
    """
    Save a debug screenshot with timestamp.

    Args:
        page: Playwright Page object
        name: Base name for the screenshot file
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_dir = "debug_screenshots"
    os.makedirs(screenshot_dir, exist_ok=True)

    filename = f"{screenshot_dir}/{name}_{timestamp}.png"
    await page.screenshot(path=filename, full_page=True)
    print(f"📸 Debug screenshot saved: {filename}")
    return filename
