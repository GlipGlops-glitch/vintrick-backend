"""
Common Selectors for New UI
Iframe and loader selectors used across the new UI

Author: GlipGlops-glitch
Created: 2025-01-19
"""


class IframeSelectors:
    """Selectors for iframes in the new Vintrace UI"""

    # Main iframe selectors
    IFRAME_MAIN = [
        "iframe[id^='Iframe_']",  # Primary pattern with UUID
        "iframe.iFrameMax",  # Class-based selector
        "iframe[vxiframeid]",  # Has vxiframeid attribute
    ]


class LoaderSelectors:
    """Selectors for loading indicators in the new UI"""

    # Loader div selectors
    LOADER_DIVS = [
        "div[id^='loader_Iframe_']",  # New UI loader pattern
    ]

    # Additional loading indicators discovered from codegen
    LOADING_INDICATORS = [
        "cell:has-text('Loading...')",
        "#megaFrame:has-text('Loading...')",
        ".vintraceLoaderText",
        ".ui-widget-content.pe-blockui-content",
    ]
