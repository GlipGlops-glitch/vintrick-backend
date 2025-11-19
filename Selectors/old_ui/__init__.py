"""
Vintrace Old UI Selectors Package
Organized selectors for the old Vintrace UI interface

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Usage:
    from Selectors.old_ui import Navigation, Reports, Common
    
    # Access selectors
    reports_icon = Navigation.NavigationSelectors.REPORTS_ICON
    product_analysis = Reports.ReportsSelectors.PRODUCT_ANALYSIS_CATEGORY
    iframe = Common.IframeSelectors.IFRAME_MAIN
"""

# Import all selector classes for convenient access
from .common import IframeSelectors, LoaderSelectors
from .navigation import NavigationSelectors
from .reports import ReportsSelectors


# Organize by module for cleaner imports
class Common:
    """Common UI elements (iframes, loaders)"""
    Iframe = IframeSelectors
    Loader = LoaderSelectors


class Navigation:
    """Navigation elements (menus, icons)"""
    Nav = NavigationSelectors


class Reports:
    """Report configuration and generation"""
    Reports = ReportsSelectors


# Provide direct access to all selector classes
__all__ = [
    # Organized classes
    'Common',
    'Navigation',
    'Reports',
    # Individual selector classes
    'IframeSelectors',
    'LoaderSelectors',
    'NavigationSelectors',
    'ReportsSelectors',
]
