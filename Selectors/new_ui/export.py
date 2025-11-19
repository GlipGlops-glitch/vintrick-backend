"""
Vintrace New UI Export Selectors
Export and download functionality selectors

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Discovery Method: Playwright codegen + HTML analysis
Reference: tools/vintrace_selectors.py (NewUISelectors class)

Note: PrimeFaces uses colon-separated IDs (vesselsForm:vesselsDT:exportButton)
which must be escaped when used in CSS selectors
"""

from typing import List


class ExportButtonSelectors:
    """Selectors for export/download buttons"""
    
    # Main export button on vessel/barrel pages
    # Discovery: HTML analysis of vessels page
    EXPORT_BUTTON: List[str] = [
        "button#vesselsForm\\:vesselsDT\\:exportButton",  # Exact ID with escaped colon
        "button[id='vesselsForm:vesselsDT:exportButton']",  # ID via attribute selector
        "button.vin-download-btn",  # Class-based fallback
    ]


class ExportMenuSelectors:
    """Selectors for export menu options"""
    
    # Excel export menu item
    # Discovery: Playwright codegen (2025-01-18)
    EXCEL_MENU_ITEM: List[str] = [
        "link:has-text('Excel')",  # From codegen - using role
        "a[role='link']:has-text('Excel')",  # Explicit role selector
        "li#vesselsForm\\:vesselsDT\\:printOptions-excel > a.ui-submenu-link",
        "li[id='vesselsForm:vesselsDT:printOptions-excel'] > a.ui-submenu-link",
        "li.vin-exportMenuOption:has-text('Excel') > a",
    ]
    
    # Excel "All" option
    # Discovery: Playwright codegen (2025-01-18) - PRIMARY
    EXCEL_ALL_OPTION: List[str] = [
        "link:has-text('All')",  # PRIMARY - From codegen discovery 2025-01-18!
        "a[role='link']:has-text('All')",  # Explicit role-based selector
        "a#vesselsForm\\:vesselsDT\\:printOptions-excel-all",
        "a[id='vesselsForm:vesselsDT:printOptions-excel-all']",
        "li#vesselsForm\\:vesselsDT\\:printOptions-excel ul li:has-text('All') a",
    ]
    
    # Barrel Details menu item
    # Discovery: HTML analysis
    BARREL_DETAILS_MENU_ITEM: List[str] = [
        "li#vesselsForm\\:vesselsDT\\:printOptions-barrelDetails > a.ui-submenu-link",
        "li[id='vesselsForm:vesselsDT:printOptions-barrelDetails'] > a.ui-submenu-link",
        "li.vin-exportMenuOption:has-text('Barrel details') > a",
    ]
    
    # Barrel Details "All" option
    # Discovery: HTML analysis
    BARREL_DETAILS_ALL_OPTION: List[str] = [
        "a#vesselsForm\\:vesselsDT\\:printOptions-barrelDetails-all",
        "a[id='vesselsForm:vesselsDT:printOptions-barrelDetails-all']",
        "li#vesselsForm\\:vesselsDT\\:printOptions-barrelDetails ul li:has-text('All') a",
    ]
