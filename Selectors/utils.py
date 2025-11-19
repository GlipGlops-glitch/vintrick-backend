"""
Selector Utility Functions
Helper functions for working with selectors

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

This module provides utility functions for selector manipulation,
validation, and prioritization.
"""

import re
from typing import List, Any, Union, Optional


def get_selector_list(module: Any, attribute_name: str) -> List[str]:
    """
    Extract selector list from a module or class attribute.
    
    Args:
        module: The module or class containing selectors
        attribute_name: Name of the attribute containing selectors
        
    Returns:
        List of selectors (single selector wrapped in list if needed)
        
    Example:
        >>> from Selectors.new_ui import Common
        >>> selectors = get_selector_list(Common.Iframe, 'IFRAME_MAIN')
        >>> print(selectors)
        ["iframe[id^='Iframe_']", "iframe.iFrameMax", "iframe[vxiframeid]"]
    """
    selectors = getattr(module, attribute_name, [])
    if isinstance(selectors, str):
        return [selectors]
    return list(selectors) if selectors else []


def get_prioritized_selectors(
    category: str,
    ui_version: str = 'new',
    use_performance_data: bool = True
) -> List[str]:
    """
    Get selectors ordered by performance metrics.
    
    Args:
        category: Selector category (e.g., 'export_button', 'iframe')
        ui_version: UI version ('new' or 'old')
        use_performance_data: If True, order by tracked performance
        
    Returns:
        List of selectors ordered by priority
        
    Example:
        >>> selectors = get_prioritized_selectors('export_button', 'new')
        >>> # Returns selectors ordered by success rate
    """
    if use_performance_data:
        try:
            from .tracking import get_best_selectors
            best = get_best_selectors(category, limit=10)
            if best:
                return [s['selector'] for s in best]
        except Exception:
            # Fall back to default if tracking not available
            pass
    
    # Fall back to default selector order from modules
    if ui_version == 'new':
        return _get_new_ui_selectors(category)
    else:
        return _get_old_ui_selectors(category)


def _get_new_ui_selectors(category: str) -> List[str]:
    """Get default New UI selectors for a category"""
    try:
        from .new_ui import Common, Navigation, Export, Reports
        
        selector_map = {
            'iframe': Common.Iframe.IFRAME_MAIN,
            'loader': Common.Loader.LOADER_DIVS,
            'loading_indicator': Common.Loader.LOADING_INDICATORS,
            'popup_close': Common.Popup.CLOSE_BUTTONS,
            'reports_menu': Navigation.Menu.REPORTS_MENU,
            'export_button': Export.Button.EXPORT_BUTTON,
            'excel_menu': Export.Menu.EXCEL_MENU_ITEM,
            'excel_all': Export.Menu.EXCEL_ALL_OPTION,
            'barrel_details_menu': Export.Menu.BARREL_DETAILS_MENU_ITEM,
            'barrel_details_all': Export.Menu.BARREL_DETAILS_ALL_OPTION,
            'generate_button': Reports.Control.GENERATE_BUTTON,
        }
        
        return selector_map.get(category, [])
    except Exception:
        return []


def _get_old_ui_selectors(category: str) -> List[str]:
    """Get default Old UI selectors for a category (placeholder)"""
    # This would be implemented when Old UI selectors are organized
    return []


def validate_selector_format(selector: str) -> bool:
    """
    Validate a selector string for basic syntax correctness.
    
    Args:
        selector: Selector string to validate
        
    Returns:
        True if selector appears valid, False otherwise
        
    Example:
        >>> validate_selector_format("button#myBtn")
        True
        >>> validate_selector_format("")
        False
        >>> validate_selector_format("   ")
        False
    """
    if not selector or not selector.strip():
        return False
    
    # Basic validation - selector should not be just whitespace
    # and should have reasonable characters
    selector = selector.strip()
    
    # Check for common invalid patterns
    if selector.startswith('>') or selector.endswith('>'):
        return False
    
    # Check for balanced brackets
    if selector.count('[') != selector.count(']'):
        return False
    if selector.count('(') != selector.count(')'):
        return False
    
    # Allow CSS selectors, XPath, and Playwright-specific selectors
    return True


def merge_selector_lists(*lists: List[str]) -> List[str]:
    """
    Merge multiple selector lists intelligently, removing duplicates.
    Preserves order with priority given to earlier lists.
    
    Args:
        *lists: Variable number of selector lists to merge
        
    Returns:
        Merged list with duplicates removed, maintaining order
        
    Example:
        >>> list1 = ["a", "b", "c"]
        >>> list2 = ["b", "c", "d"]
        >>> list3 = ["c", "d", "e"]
        >>> merge_selector_lists(list1, list2, list3)
        ['a', 'b', 'c', 'd', 'e']
    """
    seen = set()
    merged = []
    
    for selector_list in lists:
        if selector_list:
            for selector in selector_list:
                if selector and selector not in seen:
                    seen.add(selector)
                    merged.append(selector)
    
    return merged


def normalize_selector(selector: str) -> str:
    """
    Normalize a selector string for comparison.
    
    Args:
        selector: Selector to normalize
        
    Returns:
        Normalized selector string
        
    Example:
        >>> normalize_selector("  button#btn  ")
        'button#btn'
    """
    return selector.strip() if selector else ""


def is_xpath_selector(selector: str) -> bool:
    """
    Check if a selector is an XPath expression.
    
    Args:
        selector: Selector to check
        
    Returns:
        True if selector appears to be XPath
        
    Example:
        >>> is_xpath_selector("//button[@id='myBtn']")
        True
        >>> is_xpath_selector("button#myBtn")
        False
    """
    if not selector:
        return False
    
    selector = selector.strip()
    # XPath typically starts with / or // or (
    return selector.startswith('//') or selector.startswith('/') or selector.startswith('(')


def is_text_selector(selector: str) -> bool:
    """
    Check if a selector is a Playwright text selector.
    
    Args:
        selector: Selector to check
        
    Returns:
        True if selector is a text selector
        
    Example:
        >>> is_text_selector("text=Login")
        True
        >>> is_text_selector("button#login")
        False
    """
    if not selector:
        return False
    
    selector = selector.strip()
    return selector.startswith('text=') or selector.startswith('text/')


def get_selector_type(selector: str) -> str:
    """
    Determine the type of a selector.
    
    Args:
        selector: Selector to analyze
        
    Returns:
        Selector type: 'xpath', 'text', 'role', or 'css'
        
    Example:
        >>> get_selector_type("//div[@class='test']")
        'xpath'
        >>> get_selector_type("text=Click me")
        'text'
        >>> get_selector_type("button#myBtn")
        'css'
    """
    if not selector:
        return 'unknown'
    
    selector = selector.strip()
    
    if is_xpath_selector(selector):
        return 'xpath'
    elif is_text_selector(selector):
        return 'text'
    elif selector.startswith('role='):
        return 'role'
    elif ':has-text(' in selector or ':text(' in selector:
        return 'css-text'
    else:
        return 'css'
