async def navigate_to_reports_old_ui(iframe):
    """
    Navigate to Reports section in old Vintrace UI - tries multiple methods.
    
    Args:
        iframe: Playwright Frame object (the main Vintrace iframe)
    
    Returns:
        bool: True if navigation successful, False otherwise
    """
    print("\n🔍 Navigating to Reports section...")
    
    # METHOD 1: Try the bottom quick launch bar (icon-based)
    print("  Attempting Method 1: Quick Launch Bar...")
    reports_icon_selectors = [
        "div.vintrace-quick-launch-item[title='Reports']",
        "div.vintrace-quick-launch-item[style*='reports-off.png']",
        "[title='Reports'].vintrace-quick-launch-item",
    ]
    
    # Sort by historical success
    reports_icon_selectors = get_sorted_selectors("navigate_to_reports_old_ui_quicklaunch", reports_icon_selectors)
    
    for selector in reports_icon_selectors:
        try:
            element = await iframe.query_selector(selector)
            if element:
                is_visible = await element.is_visible()
                if is_visible:
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await element.click()
                    print(f"  ✓ Clicked Reports icon in quick launch bar")
                    track_selector(
                        "navigate_to_reports_old_ui_quicklaunch",
                        selector,
                        "css",
                        "old_ui_reports_quicklaunch",
                        "Reports quick launch icon"
                    )
                    await wait_for_all_vintrace_loaders(iframe)
                    await asyncio.sleep(2)
                    print("✓ Successfully navigated to Reports section")
                    return True
        except Exception as e:
            continue
    
    print("  ✗ Quick launch bar method failed, trying Consoles menu...")
    
    # METHOD 2: Try the Consoles dropdown menu
    print("  Attempting Method 2: Consoles Menu...")
    
    # Step 1: Click on "Consoles" to open the dropdown
    consoles_selectors = [
        "td:has-text('Consoles')",
        "div:has-text('Consoles')",
        "div[id*='MenuItem']:has-text('Consoles')",
    ]
    
    # Sort by historical success
    consoles_selectors = get_sorted_selectors("navigate_to_reports_old_ui_consoles", consoles_selectors)
    
    consoles_clicked = False
    for selector in consoles_selectors:
        try:
            elements = await iframe.query_selector_all(selector)
            for element in elements:
                text = await element.inner_text()
                if "Consoles" in text.strip():
                    await element.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    await element.click()
                    print(f"  ✓ Clicked 'Consoles' menu")
                    track_selector(
                        "navigate_to_reports_old_ui_consoles",
                        selector,
                        "css",
                        "old_ui_consoles_menu",
                        "Consoles dropdown menu"
                    )
                    consoles_clicked = True
                    await asyncio.sleep(1.5)  # Wait for dropdown to appear
                    break
            if consoles_clicked:
                break
        except Exception as e:
            continue
    
    if not consoles_clicked:
        print("  ❌ ERROR: Could not click 'Consoles' menu")
        return False
    
    # Step 2: Click on "Reports..." in the dropdown
    print("  Looking for 'Reports...' in dropdown menu...")
    
    # Find all menu items and look for "Reports..."
    all_menu_items = await iframe.query_selector_all("div.vintrace-menu-item")
    
    for item in all_menu_items:
        try:
            text = await item.inner_text()
            if "Reports..." in text.strip():
                await item.scroll_into_view_if_needed()
                await asyncio.sleep(0.3)
                await item.click()
                print("  ✓ Clicked 'Reports...' from menu")
                track_selector(
                    "navigate_to_reports_old_ui_menu_item",
                    "div.vintrace-menu-item",
                    "css",
                    "old_ui_reports_menu_item",
                    "Reports menu item in Consoles dropdown"
                )
                await wait_for_all_vintrace_loaders(iframe)
                await asyncio.sleep(2)
                print("✓ Successfully navigated to Reports section")
                return True
        except Exception:
            continue
    
    print("  ❌ ERROR: All methods to navigate to Reports failed")
    return False
