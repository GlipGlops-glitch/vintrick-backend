"""
Navigation Selectors for New UI
Selectors for navigation menus and tabs in the new Vintrace UI

Author: GlipGlops-glitch
Created: 2025-01-19
"""


class NavigationSelectors:
    """Selectors for navigation in the new UI"""

    # Reports menu
    REPORTS_MENU = [
        "[id='menuform:menu-reports-cs']",  # PRIMARY - From codegen
        "a#menuform\\:menu-reports-cs",  # Exact ID with escaped colon
        "a[id='menuform:menu-reports-cs']",  # ID with attribute selector
        "li.ui-menuitem a:has-text('Reports')",
        "a.ui-menuitem-link:has-text('Reports')",
    ]

    # Top search bar
    SEARCH_INPUT = [
        "input[id^='search']",
        "input[placeholder*='Search']",
        "input.search-input",
    ]

    # Tab navigation (for vessel pages, etc.)
    TAB_FRUIT = [
        "a:has-text('Fruit')",
        "li.ui-tabs-tab a:has-text('Fruit')",
        "[role='tab']:has-text('Fruit')",
    ]

    TAB_ANALYSIS = [
        "a:has-text('Analysis')",
        "li.ui-tabs-tab a:has-text('Analysis')",
        "[role='tab']:has-text('Analysis')",
    ]
