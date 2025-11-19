"""
Common Selectors
Selectors shared across both UI versions (login, popups, etc.)

Author: GlipGlops-glitch
Created: 2025-01-19
"""


# ============================================================================
# LOGIN PAGE SELECTORS (Chakra UI)
# ============================================================================

class LoginSelectors:
    """Selectors for the login page"""

    # Login form fields
    EMAIL_INPUT = [
        "input#email",  # Primary ID
        "input[name='email'][type='email']",
        "input[placeholder='Enter email']",
        "input[type='email']",
    ]

    PASSWORD_INPUT = [
        "input#password",  # Primary ID
        "input[name='password'][type='password']",
        "input[placeholder='Enter password']",
        "input[type='password']",
    ]

    # Login button
    LOGIN_BUTTON = [
        "button[type='submit'].chakra-button:has-text('Login')",
        "button[type='submit']:has-text('Login')",
        "button.chakra-button:has-text('Login')",
        "button[type='submit']",
    ]

    # Tab navigation
    LOGIN_TAB = [
        'button[role="tab"][aria-selected="true"]:has-text("Login")',
        'button[role="tab"]:has-text("Login")',
    ]

    # Error indicators
    ERROR_INDICATORS = [
        "text='Invalid email or password'",
        "text='Login failed'",
        "text='Incorrect username or password'",
        "text='Invalid credentials'",
        "div[role='alert']",
        "#chakra-toast-manager-top >> text=/error|invalid|failed/i",
        ".chakra-alert--error",
    ]


# ============================================================================
# POPUP/MODAL SELECTORS
# ============================================================================

class PopupSelectors:
    """Selectors for popups, tours, and modals"""

    CLOSE_BUTTONS = [
        "button:has-text('End tour')",  # From codegen - PRIMARY
        "button[data-role='end']",
        ".popover button[data-role='end']",
        ".tour button[data-role='end']",
        ".popover .close",
        ".modal .close",
        "button:has-text('Close')",
        "button:has-text('×')",
    ]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_selector_list(selector_class, attribute_name):
    """
    Get a list of selectors from a selector class attribute.

    Args:
        selector_class: The selector class (e.g., LoginSelectors)
        attribute_name: Name of the attribute containing selectors

    Returns:
        list: List of selectors, or single selector wrapped in list
    """
    selectors = getattr(selector_class, attribute_name, [])
    if isinstance(selectors, str):
        return [selectors]
    return selectors
