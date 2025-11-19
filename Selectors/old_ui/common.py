"""
Vintrace Old UI Common Selectors
Common UI elements like iframes and loaders for old Vintrace interface

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Discovery Method: Analysis of tools/vintrace_playwright_analysis_report.py
Reference: tools/vintrace_helpers.py
"""

from typing import List


class IframeSelectors:
    """Selectors for main content iframe in Old UI"""
    
    # Main iframe patterns (Old UI uses similar iframe structure to New UI)
    # Discovery: From vintrace_helpers.py get_main_iframe()
    IFRAME_MAIN: List[str] = [
        "iframe[id^='Iframe_']",  # Primary pattern with UUID
        "iframe.iFrameMax",  # Class-based selector
        "iframe[vxiframeid]",  # Has vxiframeid attribute
    ]


class LoaderSelectors:
    """Selectors for loading indicators and spinners in Old UI"""
    
    # Loader div patterns
    # Discovery: From vintrace_helpers.py wait_for_all_vintrace_loaders()
    LOADER_DIVS: List[str] = [
        "div[id^='loader_Iframe_']",  # Loader pattern matching iframe IDs
    ]
    
    # Additional loader patterns
    LOADING_INDICATORS: List[str] = [
        "cell:has-text('Loading...')",
        "#megaFrame:has-text('Loading...')",
        ".vintraceLoaderText",
    ]
