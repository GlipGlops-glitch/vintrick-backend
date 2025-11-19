"""
Selectors Package
Centralized selector repository for Vintrace automation

This package organizes selectors by UI version and provides tracking capabilities
to learn which selectors work best over time.

Author: GlipGlops-glitch
Created: 2025-01-19
"""

from .tracking import track_selector_attempt
from . import new_ui
from . import old_ui
from . import common

__version__ = "1.0.0"

__all__ = [
    'track_selector_attempt',
    'new_ui',
    'old_ui',
    'common',
]
