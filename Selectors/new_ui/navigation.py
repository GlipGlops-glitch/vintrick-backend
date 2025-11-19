"""
Vintrace New UI Navigation Selectors
Menu, tabs, and navigation elements

Author: GlipGlops-glitch
Created: 2025-01-19
Last Updated: 2025-01-19

Discovery Method: Playwright codegen + HTML analysis
Reference: tools/vintrace_selectors.py (NewUISelectors class)

Note: PrimeFaces IDs use colons (:) which must be escaped in CSS selectors
"""

from typing import List


class MenuSelectors:
    """Selectors for main menu navigation"""
    
    # Reports menu item
    # Discovery: Playwright codegen (2025-01-18) - PRIMARY
    # Note: PrimeFaces uses pattern menuform:menu-{section}-cs
    REPORTS_MENU: List[str] = [
        "[id='menuform:menu-reports-cs']",  # PRIMARY - From codegen
        "a#menuform\\:menu-reports-cs",  # Exact ID with escaped colon
        "a[id='menuform:menu-reports-cs']",  # ID with attribute selector
        "li.ui-menuitem a:has-text('Reports')",
        "a.ui-menuitem-link:has-text('Reports')",
    ]


class TabSelectors:
    """Selectors for tab navigation within pages"""
    
    # Tab navigation patterns will be added as discovered
    pass
