"""
Product Analysis Report (Old UI)
Downloads analysis data export CSV from Vintrace old interface

Author: GlipGlops-glitch
Created: 2025-01-19 (refactored from tools/vintrace_playwright_analysis_report.py)
"""

import asyncio
import os
import shutil
import time
from datetime import datetime
from typing import Optional
from playwright.async_api import Page

from ReportsVintrace.common.base_report import OldUIReport
from ReportsVintrace.common.helpers import (
    get_main_iframe,
    wait_for_all_vintrace_loaders,
    navigate_to_reports_old_ui,
    find_report_strip_by_title,
    save_debug_screenshot,
)
from ReportsVintrace.config import DOWNLOAD_TIMEOUT, SELECTOR_TIMEOUT
from Selectors.old_ui.reports import ReportsSelectors
from Selectors.tracking import track_selector_attempt


class AnalysisReport(OldUIReport):
    """Download Product Analysis data export from old Vintrace UI"""
    
    def __init__(self, headless: bool = False, download_dir: Optional[str] = None):
        super().__init__(headless=headless, download_dir=download_dir)
        self.default_download_dir = download_dir or "Main/data/vintrace_reports/analysis/"
        if not self.download_dir:
            self.download_dir = self.default_download_dir
        # Ensure download directory exists
        os.makedirs(self.download_dir, exist_ok=True)
    
    async def download(
        self,
        start_date: str = "08/01/2025",
        end_date: Optional[str] = None,
        show_active_only: bool = True,
        output_filename: str = "Vintrace_analysis_export.csv"
    ) -> bool:
        """
        Download analysis data export report
        
        Args:
            start_date: Start date in MM/DD/YYYY format (default: 08/01/2025)
            end_date: End date in MM/DD/YYYY format (default: today)
            show_active_only: Whether to show only active products (default: True)
            output_filename: Name for the downloaded file (default: Vintrace_analysis_export.csv)
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "=" * 60)
        print("STEP 2: DOWNLOADING ANALYSIS DATA EXPORT REPORT")
        print("=" * 60)
        
        # Verify we're on the old Vintrace URL
        current_url = self.page.url
        print(f"Current URL: {current_url}")
        if "oldVintrace=true" in current_url:
            print("✓ Confirmed: Using OLD Vintrace UI")
        else:
            print("⚠ WARNING: May not be on old Vintrace UI")
        
        # Get the main iframe where all content is
        iframe = await get_main_iframe(self.page)
        
        # Wait for page to be ready
        print("⏳ Ensuring page is ready before starting...")
        await wait_for_all_vintrace_loaders(iframe)
        await asyncio.sleep(3)
        
        # Step 1: Navigate to Reports section
        success = await navigate_to_reports_old_ui(iframe)
        if not success:
            print("❌ ERROR: Could not navigate to Reports section")
            await save_debug_screenshot(self.page, "reports_section_error")
            return False
        
        # Step 2: Click on "Product analysis" category
        print("\n🔍 Navigating to 'Product analysis' category...")
        product_analysis_selectors = ReportsSelectors.PRODUCT_ANALYSIS_CATEGORY
        
        clicked_product_analysis = False
        for selector in product_analysis_selectors:
            start_time = time.time()
            try:
                await iframe.wait_for_selector(selector, timeout=SELECTOR_TIMEOUT, state="visible")
                element = await iframe.query_selector(selector)
                
                if element:
                    # Verify exact text match
                    text = await element.inner_text()
                    if text.strip() == "Product analysis":
                        await element.scroll_into_view_if_needed()
                        await asyncio.sleep(0.5)
                        await element.click()
                        time_ms = (time.time() - start_time) * 1000
                        print(f"✓ Clicked 'Product analysis' using selector: {selector}")
                        track_selector_attempt(
                            category="product_analysis_category",
                            selector=selector,
                            success=True,
                            time_ms=time_ms,
                            context="old_ui_reports"
                        )
                        clicked_product_analysis = True
                        await wait_for_all_vintrace_loaders(iframe)
                        await asyncio.sleep(2)
                        break
            except Exception as e:
                time_ms = (time.time() - start_time) * 1000
                track_selector_attempt(
                    category="product_analysis_category",
                    selector=selector,
                    success=False,
                    time_ms=time_ms,
                    context="old_ui_reports"
                )
                print(f"  ✗ Failed with selector '{selector}': {e}")
                continue
        
        if not clicked_product_analysis:
            print("❌ ERROR: Could not navigate to 'Product analysis' category")
            await save_debug_screenshot(self.page, "product_analysis_error")
            return False
        
        # Step 3: Find the "Analysis data export" report strip
        print("\n🔍 Looking for 'Analysis data export' report...")
        report_strip = await find_report_strip_by_title(iframe, "Analysis data export")
        
        if not report_strip:
            print("❌ ERROR: Could not find 'Analysis data export' report")
            await save_debug_screenshot(self.page, "analysis_report_not_found")
            return False
        
        print("✓ Found 'Analysis data export' report strip")
        
        # Step 4: Set the "From" date
        print(f"\n📅 Setting 'From' date to {start_date}...")
        date_inputs = await report_strip.query_selector_all("input.input-date, input[type='text'][id*='c_']")
        
        from_date_set = False
        if len(date_inputs) > 0:
            start_time = time.time()
            try:
                date_input = date_inputs[0]  # First date input is "From"
                
                # Clear and fill
                await date_input.click()
                await asyncio.sleep(0.3)
                await date_input.fill("")
                await asyncio.sleep(0.3)
                await date_input.fill(start_date)
                await asyncio.sleep(0.5)
                await date_input.press("Tab")
                await asyncio.sleep(0.5)
                
                time_ms = (time.time() - start_time) * 1000
                print(f"✓ Set 'From' date to {start_date}")
                track_selector_attempt(
                    category="date_input",
                    selector=ReportsSelectors.DATE_INPUT[0],
                    success=True,
                    time_ms=time_ms,
                    context="old_ui_reports_from_date"
                )
                from_date_set = True
            except Exception as e:
                time_ms = (time.time() - start_time) * 1000
                track_selector_attempt(
                    category="date_input",
                    selector=ReportsSelectors.DATE_INPUT[0],
                    success=False,
                    time_ms=time_ms,
                    context="old_ui_reports_from_date"
                )
                print(f"  ✗ Failed to set 'From' date: {e}")
        
        if not from_date_set:
            print("⚠ WARNING: Could not set 'From' date, continuing with default...")
        
        # Step 5: Set the "To" date
        if end_date is None:
            end_date = datetime.now().strftime("%m/%d/%Y")
        
        print(f"\n📅 Setting 'To' date to {end_date}...")
        to_date_set = False
        if len(date_inputs) > 1:
            start_time = time.time()
            try:
                date_input = date_inputs[1]  # Second date input is "To"
                
                await date_input.click()
                await asyncio.sleep(0.3)
                await date_input.fill("")
                await asyncio.sleep(0.3)
                await date_input.fill(end_date)
                await asyncio.sleep(0.5)
                await date_input.press("Tab")
                await asyncio.sleep(0.5)
                
                time_ms = (time.time() - start_time) * 1000
                print(f"✓ Set 'To' date to {end_date}")
                track_selector_attempt(
                    category="date_input",
                    selector=ReportsSelectors.DATE_INPUT[0],
                    success=True,
                    time_ms=time_ms,
                    context="old_ui_reports_to_date"
                )
                to_date_set = True
            except Exception as e:
                time_ms = (time.time() - start_time) * 1000
                track_selector_attempt(
                    category="date_input",
                    selector=ReportsSelectors.DATE_INPUT[0],
                    success=False,
                    time_ms=time_ms,
                    context="old_ui_reports_to_date"
                )
                print(f"  ✗ Failed to set 'To' date: {e}")
        
        if not to_date_set:
            print("⚠ WARNING: Could not set 'To' date, continuing with default...")
        
        # Step 6: Check "Show active only" checkbox if requested
        if show_active_only:
            print("\n☑️  Checking 'Show active only' checkbox...")
            checkbox_checked = await self._check_active_only_checkbox(report_strip)
            if not checkbox_checked:
                print("⚠ WARNING: Could not check 'Show active only', continuing anyway...")
        
        # Wait for form to update
        await asyncio.sleep(1)
        
        # Step 7: Click the "Generate..." button
        print("\n📊 Clicking 'Generate...' button...")
        generate_success = await self._click_generate_button(report_strip, output_filename)
        
        if generate_success:
            print("=" * 60)
            return True
        else:
            print("❌ ERROR: Could not click 'Generate...' button or download failed")
            await save_debug_screenshot(self.page, "generate_button_error")
            print("=" * 60)
            return False
    
    async def _check_active_only_checkbox(self, report_strip) -> bool:
        """
        Helper method to check the "Show active only" checkbox.
        
        Args:
            report_strip: The report strip element
            
        Returns:
            bool: True if checkbox was checked, False otherwise
        """
        checkbox_selectors = ReportsSelectors.SHOW_ACTIVE_ONLY
        
        for selector in checkbox_selectors:
            start_time = time.time()
            try:
                # Find elements with the checkbox text
                elements = await report_strip.query_selector_all(selector)
                
                for element in elements:
                    text = await element.inner_text()
                    if "Show active only" in text:
                        # Look for checkbox image nearby
                        checkbox_img = await element.query_selector("img[src*='Checkbox'], img[id*='stateicon']")
                        
                        if not checkbox_img:
                            # Try parent/ancestor
                            parent = await element.evaluate_handle("el => el.closest('tr') || el.closest('div') || el.closest('td')")
                            if parent:
                                checkbox_img = await parent.query_selector("img[src*='Checkbox'], img[id*='stateicon']")
                        
                        if checkbox_img:
                            img_src = await checkbox_img.get_attribute("src")
                            
                            if img_src and "CheckboxOff" in img_src:
                                # Click the checkbox (or its parent div)
                                checkbox_parent = await checkbox_img.evaluate_handle("el => el.closest('div.checkbox-text') || el.parentElement")
                                if checkbox_parent:
                                    await checkbox_parent.scroll_into_view_if_needed()
                                    await asyncio.sleep(0.3)
                                    await checkbox_parent.click()
                                    await asyncio.sleep(0.5)
                                    time_ms = (time.time() - start_time) * 1000
                                    print(f"✓ Checked 'Show active only'")
                                    track_selector_attempt(
                                        category="show_active_checkbox",
                                        selector=selector,
                                        success=True,
                                        time_ms=time_ms,
                                        context="old_ui_reports"
                                    )
                                else:
                                    await checkbox_img.click()
                                    time_ms = (time.time() - start_time) * 1000
                                    print(f"✓ Checked 'Show active only' (clicked image)")
                                    track_selector_attempt(
                                        category="show_active_checkbox",
                                        selector=selector,
                                        success=True,
                                        time_ms=time_ms,
                                        context="old_ui_reports"
                                    )
                            else:
                                time_ms = (time.time() - start_time) * 1000
                                print(f"✓ 'Show active only' already checked")
                                track_selector_attempt(
                                    category="show_active_checkbox",
                                    selector=selector,
                                    success=True,
                                    time_ms=time_ms,
                                    context="old_ui_reports"
                                )
                            
                            return True
                        
            except Exception as e:
                time_ms = (time.time() - start_time) * 1000
                track_selector_attempt(
                    category="show_active_checkbox",
                    selector=selector,
                    success=False,
                    time_ms=time_ms,
                    context="old_ui_reports"
                )
                print(f"  ✗ Failed with selector '{selector}': {e}")
                continue
        
        return False
    
    async def _click_generate_button(self, report_strip, output_filename: str) -> bool:
        """
        Helper method to click the Generate button and handle download.
        
        Args:
            report_strip: The report strip element
            output_filename: Name for the downloaded file
            
        Returns:
            bool: True if download successful, False otherwise
        """
        generate_button_selectors = ReportsSelectors.GENERATE_BUTTON
        
        for selector in generate_button_selectors:
            start_time = time.time()
            try:
                button = await report_strip.query_selector(selector)
                
                if button:
                    await button.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    
                    # Set up download listener on the PAGE (not iframe)
                    async with self.page.expect_download(timeout=DOWNLOAD_TIMEOUT) as download_info:
                        await button.click()
                        print(f"✓ Clicked 'Generate...' button using selector: {selector}")
                    
                    # Wait for download to complete
                    download = await download_info.value
                    temp_path = await download.path()
                    
                    # Save directly to final location
                    final_path = os.path.join(self.download_dir, output_filename)
                    
                    if os.path.exists(final_path):
                        os.remove(final_path)
                    
                    shutil.move(temp_path, final_path)
                    time_ms = (time.time() - start_time) * 1000
                    print(f"✓ Downloaded file")
                    print(f"✓ Report saved to: {final_path}")
                    track_selector_attempt(
                        category="generate_button",
                        selector=selector,
                        success=True,
                        time_ms=time_ms,
                        context="old_ui_reports"
                    )
                    return True
                    
            except Exception as e:
                time_ms = (time.time() - start_time) * 1000
                track_selector_attempt(
                    category="generate_button",
                    selector=selector,
                    success=False,
                    time_ms=time_ms,
                    context="old_ui_reports"
                )
                print(f"  ✗ Failed with selector '{selector}': {e}")
                continue
        
        return False
