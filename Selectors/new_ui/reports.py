"""
Vintrace New UI Report Selectors
Report-specific selectors for configuration and generation

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Discovery Method: HTML analysis + Playwright codegen
Reference: tools/vintrace_selectors.py (ReportSelectors class)

Note: Report selectors span both New and Old UI since reports
can be accessed from both interfaces
"""

from typing import List


class ReportCategorySelectors:
    """Selectors for report category navigation"""
    
    # Vintage/Harvest category tab
    # Discovery: HTML analysis
    VINTAGE_HARVEST_TAB: List[str] = [
        "span:text('Vintage/Harvest')",
        "div:text('Vintage/Harvest')",
        "td:text('Vintage/Harvest')",
        "tr:has-text('Vintage/Harvest')",
        "[id$='|Text']:text('Vintage/Harvest')",
    ]
    
    # Product Analysis category
    # Discovery: HTML analysis
    PRODUCT_ANALYSIS_CATEGORY: List[str] = [
        "span:text('Product analysis')",
        "div:text('Product analysis')",
        "td:text('Product analysis')",
        "[id$='|Text']:text('Product analysis')",
    ]


class ReportFormatSelectors:
    """Selectors for report format selection"""
    
    # Format dropdown
    # Discovery: HTML analysis
    FORMAT_DROPDOWN: str = "select"


class ReportControlSelectors:
    """Selectors for report generation controls"""
    
    # Show active only checkbox
    # Discovery: HTML analysis
    SHOW_ACTIVE_ONLY: List[str] = [
        "div.checkbox-text:has-text('Show active only')",
        "table:has-text('Show active only') img[src*='Checkbox']",
        "*:has-text('Show active only')",
    ]
    
    # Report strip container
    # Discovery: HTML analysis
    REPORT_STRIP: str = "div.reportStrip"
    
    # Generate buttons
    # Discovery: HTML analysis
    GENERATE_BUTTON: List[str] = [
        "button:has-text('Generate')",
        "button:has-text('Generate...')",
        "input[type='button'][value*='Generate']",
        "button.inlineButton.positiveAction",
    ]
