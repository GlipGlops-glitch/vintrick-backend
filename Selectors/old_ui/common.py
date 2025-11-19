"""
Common Selectors for Old UI
Loader and iframe selectors for the legacy UI

Author: GlipGlops-glitch
Created: 2025-01-19
"""


class LoaderSelectors:
    """Selectors for loading indicators in the old UI"""

    # Old UI specific loaders
    LOADER_LONG = "#serverDelayMessageLong"
    LOADER_MAIN = "#serverDelayMessage"

    # All loaders combined
    ALL_LOADERS = [
        "#serverDelayMessageLong",
        "#serverDelayMessage",
    ]
