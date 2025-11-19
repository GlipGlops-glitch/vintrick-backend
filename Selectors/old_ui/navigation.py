"""
Navigation Selectors for Old UI
Selectors for navigation in the legacy UI

Author: GlipGlops-glitch
Created: 2025-01-19
"""


class NavigationSelectors:
    """Selectors for navigation in the old UI"""

    # Quick launch icons
    REPORTS_ICON = [
        "#c_170",  # Primary ID selector
        "div[title='Reports']",  # Title attribute selector
        "div.vintrace-quick-launch-item[title='Reports']",  # Quick launch specific
        "div.vintrace-quick-launch-item[style*='reports-off.png']",  # By background image
        "[title='Reports'].vintrace-quick-launch-item",  # Combined selector
    ]

    # Window controls
    WINDOW_CLOSE_BUTTON = [
        "div.echo2-window-pane-close",
        "div[id$='_close'].echo2-window-pane-close",
        "div.echo2-window-pane-close img[src*='close']",
    ]
