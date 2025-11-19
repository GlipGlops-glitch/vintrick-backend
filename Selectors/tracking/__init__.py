"""
Selector Performance Tracking Package
Track and analyze selector performance metrics

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Usage:
    from Selectors.tracking import track_selector_attempt, get_best_selectors
    
    # Track an attempt
    track_selector_attempt(
        category="export_button",
        selector="button#exportBtn",
        success=True,
        time_ms=125.5,
        context="vessels_page"
    )
    
    # Get best performers
    best = get_best_selectors("export_button", limit=3)
"""

from .selector_performance import (
    SelectorPerformanceTracker,
    SelectorAttempt,
    SelectorStats,
    track_selector_attempt,
    get_best_selectors,
    get_selector_stats,
    export_stats_report,
)

__all__ = [
    'SelectorPerformanceTracker',
    'SelectorAttempt',
    'SelectorStats',
    'track_selector_attempt',
    'get_best_selectors',
    'get_selector_stats',
    'export_stats_report',
]
