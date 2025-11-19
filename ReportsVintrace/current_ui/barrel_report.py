"""
Barrel Report Downloader (New UI)
Downloads all barrel details as CSV from current Vintrace UI

Production Ready - Refactored to use new Selectors system

Author: GlipGlops-glitch
Created: 2025-01-19

Usage:
    >>> import asyncio
    >>> from ReportsVintrace.current_ui.barrel_report import BarrelReport
    >>>
    >>> async def main():
    ...     async with BarrelReport(headless=False) as report:
    ...         await report.login()
    ...         await report.download()
    >>>
    >>> asyncio.run(main())

Or run directly:
    python -m ReportsVintrace.current_ui.barrel_report
"""

import asyncio
import os
import shutil
import datetime
from typing import Optional

from ReportsVintrace.common.base_report import NewUIReport
from Selectors.new_ui.export import ExportSelectors
from Selectors.tracking import track_selector_attempt
from ReportsVintrace.config import DOWNLOAD_TIMEOUT


class BarrelReport(NewUIReport):
    """
    Download all barrel details as CSV from current Vintrace UI.
    
    This report:
    1. Clicks the Export button
    2. Selects Barrel details export
    3. Downloads all barrel data
    """

    def __init__(self, headless: bool = False, download_dir: Optional[str] = None):
        """
        Initialize the barrel report downloader.

        Args:
            headless: Run browser in headless mode
            download_dir: Custom download directory (uses default if None)
        """
        super().__init__(
            headless=headless,
            download_dir=download_dir,
            report_type="barrels"
        )

    async def download(self, output_filename: str = "Vintrace_all_barrels.csv") -> bool:
        """
        Download the barrel details report.

        Args:
            output_filename: Name for the output CSV file

        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "=" * 60)
        print("DOWNLOADING BARREL DETAILS REPORT")
        print("=" * 60)

        if not self.iframe:
            print("❌ ERROR: No iframe available. Did you call login()?")
            return False

        # Wait for page to be ready
        print("⏳ Ensuring page is ready...")
        await self.wait_for_loaders()
        await asyncio.sleep(3)

        # Scroll to bottom to ensure UI elements are loaded
        print("📜 Scrolling to bottom of page...")
        try:
            await self.iframe.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            print("✓ Scrolled to bottom")
        except Exception as e:
            print(f"  ⚠ Could not scroll: {e}")

        # Step 1: Click the export button
        if not await self._click_export_button():
            return False

        # Step 2: Click "Barrel details" in the menu
        if not await self._click_barrel_details_menu():
            return False

        # Step 3: Click "All" to download the report
        return await self._download_all_barrels(output_filename)

    async def _click_export_button(self) -> bool:
        """Click the export button."""
        print("\nAttempting to click export button...")

        for selector in ExportSelectors.EXPORT_BUTTON:
            start_time = datetime.datetime.now()
            try:
                await self.iframe.wait_for_selector(selector, timeout=10_000, state="attached")
                export_btn = await self.iframe.query_selector(selector)
                
                if export_btn:
                    await export_btn.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)

                    if not await export_btn.is_visible():
                        print(f"  ⚠ Button found but not visible with selector: {selector}")
                        continue

                    await export_btn.click()
                    elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
                    print(f"✓ Clicked export button using selector: {selector}")
                    
                    track_selector_attempt(
                        category="export_button",
                        selector=selector,
                        success=True,
                        time_ms=elapsed_ms,
                        context="barrels_new_ui",
                        notes="Export button in vessels/barrels page"
                    )
                    
                    await asyncio.sleep(1.5)
                    return True
                    
            except Exception as e:
                elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
                track_selector_attempt(
                    category="export_button",
                    selector=selector,
                    success=False,
                    time_ms=elapsed_ms,
                    context="barrels_new_ui"
                )
                print(f"  ✗ Failed with selector '{selector}': {e}")
                continue

        print("❌ ERROR: Could not click export button")
        await self.screenshot("export_button_error")
        return False

    async def _click_barrel_details_menu(self) -> bool:
        """Click the Barrel details menu item."""
        print("\nAttempting to click 'Barrel details' menu item...")

        for selector in ExportSelectors.BARREL_DETAILS_MENU_ITEM:
            start_time = datetime.datetime.now()
            try:
                await self.iframe.wait_for_selector(selector, timeout=10_000, state="visible")
                barrel_link = await self.iframe.query_selector(selector)

                if barrel_link:
                    await barrel_link.scroll_into_view_if_needed()
                    await asyncio.sleep(0.3)

                    await barrel_link.click()
                    elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
                    print(f"✓ Clicked 'Barrel details' using selector: {selector}")
                    
                    track_selector_attempt(
                        category="barrel_details_menu",
                        selector=selector,
                        success=True,
                        time_ms=elapsed_ms,
                        context="barrels_new_ui",
                        notes="Barrel details menu item"
                    )
                    
                    await asyncio.sleep(1)
                    return True
                    
            except Exception as e:
                elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
                track_selector_attempt(
                    category="barrel_details_menu",
                    selector=selector,
                    success=False,
                    time_ms=elapsed_ms,
                    context="barrels_new_ui"
                )
                print(f"  ✗ Failed with selector '{selector}': {e}")
                continue

        print("❌ ERROR: Could not click 'Barrel details' menu item")
        await self.screenshot("barrel_details_menu_error")
        return False

    async def _download_all_barrels(self, output_filename: str) -> bool:
        """Download all barrels by clicking the 'All' option."""
        print("\nAttempting to click 'All' to download report...")

        for selector in ExportSelectors.BARREL_DETAILS_ALL_OPTION:
            start_time = datetime.datetime.now()
            try:
                await self.iframe.wait_for_selector(selector, timeout=10_000, state="attached")
                all_option = await self.iframe.query_selector(selector)

                if all_option:
                    # Check visibility
                    is_visible = await all_option.is_visible()
                    if not is_visible:
                        print(f"  ⚠ 'All' option found but not visible, waiting...")
                        await asyncio.sleep(1)
                        is_visible = await all_option.is_visible()
                        if not is_visible:
                            print(f"  ✗ 'All' option still not visible with selector: {selector}")
                            continue

                    await all_option.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)

                    # Set up download listener on the page (not iframe)
                    async with self.page.expect_download(timeout=DOWNLOAD_TIMEOUT) as download_info:
                        await all_option.click(force=True)
                        elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
                        print(f"✓ Clicked 'All' option using selector: {selector}")
                        
                        track_selector_attempt(
                            category="barrel_all_option",
                            selector=selector,
                            success=True,
                            time_ms=elapsed_ms,
                            context="barrels_new_ui",
                            notes="All option for barrel details"
                        )

                    # Wait for download to complete
                    download = await download_info.value
                    temp_path = await download.path()

                    # Save the file
                    final_path = os.path.join(self.download_dir, output_filename)
                    if os.path.exists(final_path):
                        os.remove(final_path)
                    shutil.move(temp_path, final_path)
                    
                    print(f"✓ Report saved to: {final_path}")
                    print("=" * 60)
                    return True

            except Exception as e:
                elapsed_ms = (datetime.datetime.now() - start_time).total_seconds() * 1000
                track_selector_attempt(
                    category="barrel_all_option",
                    selector=selector,
                    success=False,
                    time_ms=elapsed_ms,
                    context="barrels_new_ui"
                )
                print(f"  ✗ Failed with selector '{selector}': {e}")
                continue

        print("❌ ERROR: Could not click 'All' option or download failed")
        await self.screenshot("download_all_error")
        return False


# ============================================================================
# STANDALONE EXECUTION
# ============================================================================

async def main():
    """Standalone execution example."""
    async with BarrelReport(headless=False) as report:
        # Login
        if not await report.login():
            print("❌ Login failed")
            return

        # Download report
        if not await report.download():
            print("❌ Download failed")
            return

        print("\n" + "=" * 60)
        print("✓ ALL STEPS COMPLETED SUCCESSFULLY")
        print("=" * 60)

        # Brief pause for inspection
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
