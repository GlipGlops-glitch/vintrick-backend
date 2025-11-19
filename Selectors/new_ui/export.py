"""
Export Selectors for New UI
Selectors for export buttons and menus in the new Vintrace UI

Author: GlipGlops-glitch
Created: 2025-01-19
"""


class ExportSelectors:
    """Selectors for export functionality in the new UI"""

    # Export button (main)
    EXPORT_BUTTON = [
        "button#vesselsForm\\:vesselsDT\\:exportButton",  # Exact ID with escaped colon
        "button[id='vesselsForm:vesselsDT:exportButton']",  # ID via attribute selector
        "button.vin-download-btn",  # Class-based fallback
    ]

    # Barrel details menu options
    BARREL_DETAILS_MENU_ITEM = [
        "li#vesselsForm\\:vesselsDT\\:printOptions-barrelDetails > a.ui-submenu-link",
        "li[id='vesselsForm:vesselsDT:printOptions-barrelDetails'] > a.ui-submenu-link",
        "li.vin-exportMenuOption:has-text('Barrel details') > a",
    ]

    BARREL_DETAILS_ALL_OPTION = [
        "a#vesselsForm\\:vesselsDT\\:printOptions-barrelDetails-all",
        "a[id='vesselsForm:vesselsDT:printOptions-barrelDetails-all']",
        "li#vesselsForm\\:vesselsDT\\:printOptions-barrelDetails ul li:has-text('All') a",
    ]

    # Excel export menu options
    EXCEL_MENU_ITEM = [
        "link:has-text('Excel')",  # From codegen - using role
        "a[role='link']:has-text('Excel')",  # Explicit role selector
        "li#vesselsForm\\:vesselsDT\\:printOptions-excel > a.ui-submenu-link",
        "li[id='vesselsForm:vesselsDT:printOptions-excel'] > a.ui-submenu-link",
        "li.vin-exportMenuOption:has-text('Excel') > a",
    ]

    EXCEL_ALL_OPTION = [
        "link:has-text('All')",  # PRIMARY - From codegen discovery 2025-01-18!
        "a[role='link']:has-text('All')",  # Explicit role-based selector
        "a#vesselsForm\\:vesselsDT\\:printOptions-excel-all",
        "a[id='vesselsForm:vesselsDT:printOptions-excel-all']",
        "li#vesselsForm\\:vesselsDT\\:printOptions-excel ul li:has-text('All') a",
    ]

    # Vessel details export
    VESSEL_DETAILS_MENU_ITEM = [
        "li#vesselsForm\\:vesselsDT\\:printOptions-vesselDetails > a.ui-submenu-link",
        "li[id='vesselsForm:vesselsDT:printOptions-vesselDetails'] > a.ui-submenu-link",
        "li.vin-exportMenuOption:has-text('Vessel details') > a",
    ]

    VESSEL_DETAILS_ALL_OPTION = [
        "a#vesselsForm\\:vesselsDT\\:printOptions-vesselDetails-all",
        "a[id='vesselsForm:vesselsDT:printOptions-vesselDetails-all']",
        "li#vesselsForm\\:vesselsDT\\:printOptions-vesselDetails ul li:has-text('All') a",
    ]
