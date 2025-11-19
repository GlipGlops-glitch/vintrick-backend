"""
ReportsVintrace Common Module
Shared functionality for all Vintrace reports

Author: GlipGlops-glitch
Created: 2025-01-19
"""

from .base_report import BaseReport, OldUIReport
from .helpers import (
    wait_for_all_vintrace_loaders,
    get_main_iframe,
    navigate_to_reports_old_ui,
    find_report_strip_by_title,
    save_debug_screenshot,
)

__all__ = [
    'BaseReport',
    'OldUIReport',
    'wait_for_all_vintrace_loaders',
    'get_main_iframe',
    'navigate_to_reports_old_ui',
    'find_report_strip_by_title',
    'save_debug_screenshot',
]
