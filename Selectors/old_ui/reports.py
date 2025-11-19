"""
Vintrace Old UI Report Selectors
Report-specific selectors for old Vintrace interface

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Discovery Method: Analysis of tools/vintrace_playwright_analysis_report.py
"""

from typing import List


class ReportsSelectors:
    """Selectors for report configuration and generation in Old UI"""
    
    # Product Analysis category
    # Discovery: From vintrace_playwright_analysis_report.py download_analysis_report()
    PRODUCT_ANALYSIS_CATEGORY: List[str] = [
        "span:text('Product analysis')",
        "div:text('Product analysis')",
        "td:text('Product analysis')",
        "[id$='|Text']:text('Product analysis')",
        "xpath=//*[text()='Product analysis']",  # XPath fallback
    ]
    
    # Report strip container
    # Discovery: From find_report_strip_by_title() in vintrace_helpers.py
    REPORT_STRIP: str = "div.reportStrip"
    
    # Date input fields
    # Discovery: From vintrace_playwright_analysis_report.py
    DATE_INPUT: List[str] = [
        "input.input-date",
        "input[type='text'][id*='c_']",
    ]
    
    # Show active only checkbox
    # Discovery: From vintrace_playwright_analysis_report.py
    SHOW_ACTIVE_ONLY: List[str] = [
        "div.checkbox-text:has-text('Show active only')",
        "table:has-text('Show active only') img[src*='Checkbox']",
        "*:has-text('Show active only')",
    ]
    
    # Checkbox image patterns (for detecting checkbox state)
    CHECKBOX_IMAGE: List[str] = [
        "img[src*='Checkbox']",
        "img[id*='stateicon']",
    ]
    
    # Generate buttons
    # Discovery: From vintrace_playwright_analysis_report.py
    GENERATE_BUTTON: List[str] = [
        "button:has-text('Generate')",
        "button:has-text('Generate...')",
        "input[type='button'][value*='Generate']",
        "button.inlineButton.positiveAction",
    ]
