"""
New UI Selectors Package
Selectors for the current/new Vintrace UI (PrimeFaces framework)

Author: GlipGlops-glitch
Created: 2025-01-19
"""

from .common import IframeSelectors, LoaderSelectors
from .export import ExportSelectors
from .navigation import NavigationSelectors

__all__ = [
    'IframeSelectors',
    'LoaderSelectors',
    'ExportSelectors',
    'NavigationSelectors',
]
