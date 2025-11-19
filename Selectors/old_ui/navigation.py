"""
Vintrace Old UI Navigation Selectors
Navigation elements for old Vintrace interface

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Discovery Method: Analysis of tools/vintrace_helpers.py navigate_to_reports_old_ui()
"""

from typing import List


class NavigationSelectors:
    """Selectors for main navigation in Old UI"""
    
    # Reports icon/button in quick launch area
    # Discovery: From vintrace_helpers.py navigate_to_reports_old_ui()
    # Note: Old UI uses image-based navigation
    REPORTS_ICON: List[str] = [
        "img[src*='Reports.gif']",  # Primary - Image-based navigation
        "img[title*='Reports']",  # Image with Reports title
        "a:has(img[src*='Reports.gif'])",  # Link containing Reports image
        "img[id*='Reports']",  # Image with Reports in ID
    ]
