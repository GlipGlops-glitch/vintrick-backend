"""
Vintrace Selector Management System
Centralized, organized selector repository for Vintrace automation

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

This package provides a clean, organized system for managing Vintrace UI selectors
with performance tracking and intelligent selector prioritization.

Quick Start:
    # Import organized selectors
    from Selectors import NewUI
    
    # Access specific selectors
    iframe = NewUI.Common.Iframe.IFRAME_MAIN
    export_btn = NewUI.Export.Button.EXPORT_BUTTON
    reports = NewUI.Navigation.Menu.REPORTS_MENU
    
    # Track selector performance
    from Selectors import track_selector_attempt, get_best_selectors
    
    track_selector_attempt(
        category="export_button",
        selector="button#exportBtn",
        success=True,
        time_ms=125.5
    )
    
    best = get_best_selectors("export_button", limit=3)

Architecture:
    Selectors/
    ├── new_ui/          # New UI (PrimeFaces) selectors
    │   ├── common.py    # Iframes, loaders, popups
    │   ├── navigation.py # Menus, tabs
    │   ├── reports.py   # Report generation
    │   ├── vessels.py   # Vessel/barrel pages
    │   └── export.py    # Export functionality
    ├── tracking/        # Performance tracking
    │   └── selector_performance.py
    └── utils.py         # Helper functions
"""

# Import organized selector modules
from . import new_ui
from . import tracking
from . import utils

# Import main selector classes for convenience
from .new_ui import (
    Common,
    Navigation,
    Export,
    Reports,
    Vessels,
)

# Import tracking functions
from .tracking import (
    track_selector_attempt,
    get_best_selectors,
    get_selector_stats,
    export_stats_report,
)

# Import utility functions
from .utils import (
    get_selector_list,
    get_prioritized_selectors,
    validate_selector_format,
    merge_selector_lists,
    get_selector_type,
)


# Create convenient alias
class NewUI:
    """New UI (PrimeFaces) selectors - organized by function"""
    Common = Common
    Navigation = Navigation
    Export = Export
    Reports = Reports
    Vessels = Vessels


# Package metadata
__version__ = '1.0.0'
__author__ = 'GlipGlops-glitch'

# Public API
__all__ = [
    # Main selector classes
    'NewUI',
    'Common',
    'Navigation',
    'Export',
    'Reports',
    'Vessels',
    
    # Tracking functions
    'track_selector_attempt',
    'get_best_selectors',
    'get_selector_stats',
    'export_stats_report',
    
    # Utility functions
    'get_selector_list',
    'get_prioritized_selectors',
    'validate_selector_format',
    'merge_selector_lists',
    'get_selector_type',
    
    # Submodules
    'new_ui',
    'tracking',
    'utils',
]
