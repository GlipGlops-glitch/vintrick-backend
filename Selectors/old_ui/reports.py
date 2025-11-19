"""
Report Selectors for Old UI
Selectors specific to report configuration and generation in the legacy UI

Author: GlipGlops-glitch
Created: 2025-01-19
"""


class ReportSelectors:
    """Selectors specific to report configuration and generation"""

    # Report category navigation
    REPORT_CATEGORY_SPAN = "span[id$='|Text']"  # Pattern for category text elements

    VINTAGE_HARVEST_TAB = [
        "span:text('Vintage/Harvest')",
        "div:text('Vintage/Harvest')",
        "td:text('Vintage/Harvest')",
        "tr:has-text('Vintage/Harvest')",
        "[id$='|Text']:text('Vintage/Harvest')",
    ]

    PRODUCT_ANALYSIS_CATEGORY = [
        "span:text('Product analysis')",
        "div:text('Product analysis')",
        "td:text('Product analysis')",
        "[id$='|Text']:text('Product analysis')",
    ]

    # Report strips and controls
    REPORT_STRIP = "div.reportStrip"

    # Tables
    JX2_TABLE = "table.jx2table"

    # Generate buttons
    GENERATE_BUTTON = [
        "button:has-text('Generate')",
        "button:has-text('Generate...')",
        "input[type='button'][value*='Generate']",
        "button.inlineButton.positiveAction",
    ]

    # Checkbox patterns
    CHECKBOX_IMAGE = "img[src*='Checkbox']"
    CHECKBOX_STATE_ICON = "img[id*='stateicon']"

    # Common checkboxes
    SHOW_ACTIVE_ONLY = [
        "div.checkbox-text:has-text('Show active only')",
        "table:has-text('Show active only') img[src*='Checkbox']",
        "*:has-text('Show active only')",
    ]

    # Date inputs
    DATE_INPUT = [
        "input.input-date",
        "input[type='text'][id*='c_']",
    ]

    # Format selection
    FORMAT_DROPDOWN = "select"
