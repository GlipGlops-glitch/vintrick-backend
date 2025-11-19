"""
ReportsVintrace Package
Consolidated, maintainable Vintrace report download scripts using the Selectors system

Author: GlipGlops-glitch
Created: 2025-01-19

This package provides:
- Standardized report downloaders for Vintrace
- Integration with the Selectors tracking system
- Base classes for creating new report downloaders
- Configuration management
- Helper utilities

Usage:
    >>> import asyncio
    >>> from ReportsVintrace.current_ui.vessels_report import VesselsReport
    >>>
    >>> async def main():
    ...     async with VesselsReport(headless=False) as report:
    ...         await report.login()
    ...         await report.download()
    >>>
    >>> asyncio.run(main())
"""

from . import config
from . import common

__version__ = "1.0.0"

__all__ = [
    'config',
    'common',
]
