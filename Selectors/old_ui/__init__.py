"""
Old UI Selectors Package
Selectors for the legacy Vintrace UI (Echo2 framework)

Author: GlipGlops-glitch
Created: 2025-01-19
"""

from .common import LoaderSelectors
from .navigation import NavigationSelectors
from .reports import ReportSelectors

__all__ = [
    'LoaderSelectors',
    'NavigationSelectors',
    'ReportSelectors',
]
