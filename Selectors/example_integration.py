#!/usr/bin/env python3
"""
Example: Using the Selector Management System in Playwright Automation

This example shows how to integrate the new selector system into
existing Playwright automation scripts.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import time
from Selectors import NewUI, track_selector_attempt, get_prioritized_selectors


async def wait_for_element_with_tracking(page, category: str, selectors: list, timeout: int = 5000):
    """
    Try multiple selectors and track which ones work.
    
    Args:
        page: Playwright page object
        category: Selector category for tracking
        selectors: List of selectors to try
        timeout: Timeout in milliseconds for each attempt
        
    Returns:
        The element locator that succeeded, or None
    """
    for selector in selectors:
        start = time.time()
        try:
            # Try to locate element
            locator = page.locator(selector)
            await locator.wait_for(timeout=timeout)
            
            # Success - track it
            elapsed_ms = (time.time() - start) * 1000
            track_selector_attempt(
                category=category,
                selector=selector,
                success=True,
                time_ms=elapsed_ms,
                context=f"page_{page.url}"
            )
            
            print(f"✓ Found with: {selector} ({elapsed_ms:.1f}ms)")
            return locator
            
        except Exception as e:
            # Failed - track it
            elapsed_ms = (time.time() - start) * 1000
            track_selector_attempt(
                category=category,
                selector=selector,
                success=False,
                time_ms=elapsed_ms,
                context=f"page_{page.url}"
            )
            
            print(f"✗ Failed: {selector} ({elapsed_ms:.1f}ms)")
            continue
    
    print(f"⚠ No selectors worked for category: {category}")
    return None


async def example_vessels_page_automation(page):
    """
    Example: Automate the vessels page with selector tracking
    """
    print("\n" + "=" * 80)
    print("Example: Vessels Page Automation with Tracking")
    print("=" * 80)
    
    # Navigate to vessels page (example)
    # await page.goto("https://example.vintrace.com/vessels")
    
    # Wait for iframe using tracked selectors
    print("\n1. Waiting for main iframe...")
    iframe_locator = await wait_for_element_with_tracking(
        page,
        category="iframe_main",
        selectors=NewUI.Common.Iframe.IFRAME_MAIN,
        timeout=5000
    )
    
    # Get iframe context
    # iframe_content = await iframe_locator.content_frame()
    
    # Wait for export button using tracked selectors
    print("\n2. Waiting for export button...")
    export_btn = await wait_for_element_with_tracking(
        page,
        category="export_button",
        selectors=NewUI.Export.Button.EXPORT_BUTTON,
        timeout=3000
    )
    
    # Click export button
    # if export_btn:
    #     await export_btn.click()
    
    # Wait for Excel menu using tracked selectors
    print("\n3. Waiting for Excel menu option...")
    excel_menu = await wait_for_element_with_tracking(
        page,
        category="excel_menu",
        selectors=NewUI.Export.Menu.EXCEL_MENU_ITEM,
        timeout=2000
    )
    
    print("\n✓ Example automation complete!")


async def example_optimized_automation(page):
    """
    Example: Use performance data to optimize selector order
    """
    print("\n" + "=" * 80)
    print("Example: Optimized Automation Using Performance Data")
    print("=" * 80)
    
    # Get selectors ordered by historical performance
    print("\n1. Getting prioritized selectors based on past performance...")
    
    export_selectors = get_prioritized_selectors("export_button", ui_version="new")
    if not export_selectors:
        # Fall back to default if no performance data
        export_selectors = NewUI.Export.Button.EXPORT_BUTTON
        print("   Using default selectors (no performance data yet)")
    else:
        print(f"   Using {len(export_selectors)} selectors ordered by success rate")
    
    # Try optimized selector order
    print("\n2. Trying selectors (best performers first)...")
    export_btn = await wait_for_element_with_tracking(
        page,
        category="export_button",
        selectors=export_selectors,
        timeout=3000
    )
    
    print("\n✓ Optimized automation complete!")


def print_usage_examples():
    """Print code examples for common use cases"""
    print("\n" + "=" * 80)
    print("Common Usage Patterns")
    print("=" * 80)
    
    print("""
1. BASIC SELECTOR ACCESS:
   
   from Selectors import NewUI
   
   # Get iframe selectors
   iframe_selectors = NewUI.Common.Iframe.IFRAME_MAIN
   
   # Get export button selectors
   export_button = NewUI.Export.Button.EXPORT_BUTTON
   
   # Get reports menu selectors
   reports_menu = NewUI.Navigation.Menu.REPORTS_MENU

2. WITH PERFORMANCE TRACKING:
   
   from Selectors import NewUI, track_selector_attempt
   import time
   
   for selector in NewUI.Export.Button.EXPORT_BUTTON:
       start = time.time()
       try:
           element = await page.locator(selector).wait_for(timeout=1000)
           elapsed_ms = (time.time() - start) * 1000
           track_selector_attempt("export_button", selector, True, elapsed_ms)
           break
       except:
           elapsed_ms = (time.time() - start) * 1000
           track_selector_attempt("export_button", selector, False, elapsed_ms)

3. USING PRIORITIZED SELECTORS:
   
   from Selectors import get_prioritized_selectors
   
   # Get selectors ordered by performance
   selectors = get_prioritized_selectors("export_button", ui_version="new")
   
   # Fastest, most reliable selectors come first
   for selector in selectors:
       try:
           await page.locator(selector).wait_for(timeout=1000)
           break
       except:
           continue

4. GENERATING PERFORMANCE REPORTS:
   
   from Selectors import export_stats_report
   
   # Generate report after automation runs
   report = export_stats_report("selector_performance.txt")
   print(report)

5. VALIDATING SELECTORS:
   
   from Selectors import validate_selector_format, get_selector_type
   
   if validate_selector_format(my_selector):
       selector_type = get_selector_type(my_selector)
       print(f"Valid {selector_type} selector")
""")


def main():
    """Main example runner"""
    print("=" * 80)
    print("Selector Management System - Integration Examples")
    print("=" * 80)
    
    print_usage_examples()
    
    print("\n" + "=" * 80)
    print("To run Playwright examples, uncomment the async calls and run with:")
    print("  python -m asyncio Selectors/example_integration.py")
    print("=" * 80)
    
    # To actually run Playwright examples, you would do:
    # asyncio.run(example_vessels_page_automation(page))
    # asyncio.run(example_optimized_automation(page))


if __name__ == "__main__":
    main()
