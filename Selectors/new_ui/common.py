"""
Vintrace New UI Common Selectors
Common UI elements like iframes, loaders, and popups

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Discovery Method: HTML analysis + Playwright codegen
Reference: tools/vintrace_selectors.py (NewUISelectors class)
"""

from typing import List


class IframeSelectors:
    """Selectors for main content iframe in New UI"""
    
    # Main iframe patterns (PrimeFaces framework)
    # Discovery: HTML analysis - PrimeFaces uses UUID-based iframe IDs
    IFRAME_MAIN: List[str] = [
        "iframe[id^='Iframe_']",  # Primary pattern with UUID
        "iframe.iFrameMax",  # Class-based selector
        "iframe[vxiframeid]",  # Has vxiframeid attribute
    ]


class LoaderSelectors:
    """Selectors for loading indicators and spinners"""
    
    # Loader div patterns
    # Discovery: HTML analysis - Loader divs match iframe IDs
    LOADER_DIVS: List[str] = [
        "div[id^='loader_Iframe_']",  # New UI loader pattern
    ]
    
    # Additional loader patterns
    # Discovery: Playwright codegen (2025-01-18)
    LOADING_INDICATORS: List[str] = [
        "cell:has-text('Loading...')",
        "#megaFrame:has-text('Loading...')",
        ".vintraceLoaderText",
        ".ui-widget-content.pe-blockui-content",
    ]


class PopupSelectors:
    """Selectors for popups, tours, and modals"""
    
    # Close button patterns
    # Discovery: Playwright codegen (2025-01-18)
    CLOSE_BUTTONS: List[str] = [
        "button:has-text('End tour')",  # From codegen - PRIMARY
        "button[data-role='end']",
        ".popover button[data-role='end']",
        ".tour button[data-role='end']",
        ".popover .close",
        ".modal .close",
        "button:has-text('Close')",
        "button:has-text('×')",
    ]
