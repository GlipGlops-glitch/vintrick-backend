"""
Vintrace New UI Selectors Package
Organized selectors for the new Vintrace UI (PrimeFaces framework)

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Usage:
    from Selectors.new_ui import Navigation, Export, Common, Reports, Vessels
    
    # Access selectors
    reports_menu = Navigation.MenuSelectors.REPORTS_MENU
    export_button = Export.ExportButtonSelectors.EXPORT_BUTTON
    iframe = Common.IframeSelectors.IFRAME_MAIN
"""

# Import all selector classes for convenient access
from .common import IframeSelectors, LoaderSelectors, PopupSelectors
from .navigation import MenuSelectors, TabSelectors
from .export import ExportButtonSelectors, ExportMenuSelectors
from .reports import (
    ReportCategorySelectors,
    ReportFormatSelectors,
    ReportControlSelectors,
)
from .vessels import VesselTableSelectors


# Organize by module for cleaner imports
class Common:
    """Common UI elements (iframes, loaders, popups)"""
    Iframe = IframeSelectors
    Loader = LoaderSelectors
    Popup = PopupSelectors


class Navigation:
    """Navigation elements (menus, tabs)"""
    Menu = MenuSelectors
    Tab = TabSelectors


class Export:
    """Export and download functionality"""
    Button = ExportButtonSelectors
    Menu = ExportMenuSelectors


class Reports:
    """Report configuration and generation"""
    Category = ReportCategorySelectors
    Format = ReportFormatSelectors
    Control = ReportControlSelectors


class Vessels:
    """Vessel and barrel pages"""
    Table = VesselTableSelectors


# Provide direct access to all selector classes
__all__ = [
    # Organized classes
    'Common',
    'Navigation',
    'Export',
    'Reports',
    'Vessels',
    # Individual selector classes
    'IframeSelectors',
    'LoaderSelectors',
    'PopupSelectors',
    'MenuSelectors',
    'TabSelectors',
    'ExportButtonSelectors',
    'ExportMenuSelectors',
    'ReportCategorySelectors',
    'ReportFormatSelectors',
    'ReportControlSelectors',
    'VesselTableSelectors',
]
