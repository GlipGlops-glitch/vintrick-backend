"""
ReportsVintrace Configuration
Common configuration values for all Vintrace reports

Author: GlipGlops-glitch
Created: 2025-01-19
"""

# Timeout values (in milliseconds)
LARGE_TIMEOUT = 120000  # 2 minutes
DOWNLOAD_TIMEOUT = 1200000  # 20 minutes for large reports
SELECTOR_TIMEOUT = 120000  # 2 minutes - selector wait time
STANDARD_TIMEOUT = 30000  # 30 seconds - standard wait time
MEDIUM_TIMEOUT = 10000  # 10 seconds - medium wait time
SHORT_TIMEOUT = 5000  # 5 seconds - short wait time
LOADER_APPEAR_TIMEOUT = 15000  # 15 seconds - wait for loader to appear

# URLs
LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"
NEW_URL = "https://us61.vintrace.net/smwe/2.app"

# Directory paths
DEFAULT_DOWNLOAD_DIR = "Main/data/vintrace_reports/"
DEBUG_SCREENSHOT_DIR = "debug_screenshots/"
