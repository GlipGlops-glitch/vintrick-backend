"""
Configuration for ReportsVintrace
Default settings for report downloads

Author: GlipGlops-glitch
Created: 2025-01-19
"""

import os

# ============================================================================
# DEFAULT DOWNLOAD DIRECTORIES
# ============================================================================

DEFAULT_DOWNLOAD_DIRS = {
    'vessels': 'Main/data/vintrace_reports/vessel_details/',
    'barrels': 'Main/data/vintrace_reports/barrel_details/',
    'analysis': 'Main/data/vintrace_reports/analysis/',
    'fruit': 'Main/data/vintrace_reports/fruit/',
}

# Ensure all default directories exist
for dir_path in DEFAULT_DOWNLOAD_DIRS.values():
    os.makedirs(dir_path, exist_ok=True)


# ============================================================================
# TIMEOUT VALUES (in milliseconds)
# ============================================================================

# Download timeouts
DOWNLOAD_TIMEOUT = 300_000  # 5 minutes
LARGE_DOWNLOAD_TIMEOUT = 1_200_000  # 20 minutes for very large reports

# Selector timeouts
SELECTOR_TIMEOUT = 30_000  # 30 seconds
STANDARD_TIMEOUT = 30_000  # 30 seconds - standard wait time
MEDIUM_TIMEOUT = 10_000  # 10 seconds - medium wait time
SHORT_TIMEOUT = 5_000  # 5 seconds - short wait time
QUICK_TIMEOUT = 3_000  # 3 seconds - quick operations

# Loader timeouts
LOADER_APPEAR_TIMEOUT = 15_000  # 15 seconds - wait for loader to appear


# ============================================================================
# BROWSER SETTINGS
# ============================================================================

DEFAULT_HEADLESS = False
DEFAULT_VIEWPORT = {'width': 1920, 'height': 1080}

# Browser launch args for better compatibility
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',
]


# ============================================================================
# URLS
# ============================================================================

LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"
NEW_URL = "https://us61.vintrace.net/smwe/2.app"


# ============================================================================
# CREDENTIALS
# ============================================================================

# Credentials are loaded from environment variables
# Set these in your .env file:
# VINTRACE_EMAIL=your-email@example.com
# VINTRACE_PASSWORD=your-password
