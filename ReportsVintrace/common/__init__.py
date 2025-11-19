"""
Common Package for Vintrace Reports
Shared utilities and base classes

Author: GlipGlops-glitch
Created: 2025-01-19
"""

from .base_report import VintraceReport, NewUIReport, OldUIReport
from .helpers import (
    load_vintrace_credentials,
    initialize_browser,
    vintrace_login,
    wait_for_all_vintrace_loaders,
    get_main_iframe,
    close_popups,
    navigate_to_reports_old_ui,
    save_debug_screenshot,
)

__all__ = [
    # Base classes
    'VintraceReport',
    'NewUIReport',
    'OldUIReport',
    # Helper functions
    'load_vintrace_credentials',
    'initialize_browser',
    'vintrace_login',
    'wait_for_all_vintrace_loaders',
    'get_main_iframe',
    'close_popups',
    'navigate_to_reports_old_ui',
    'save_debug_screenshot',
]
