# Selector Management System - Quick Reference

## 🚀 Quick Import Guide

```python
# Import the main selector interface
from Selectors import NewUI

# Import tracking functions
from Selectors import track_selector_attempt, get_best_selectors

# Import utilities
from Selectors import get_prioritized_selectors, validate_selector_format
```

## 📋 Selector Categories

| Category | Path | Description |
|----------|------|-------------|
| **Iframes** | `NewUI.Common.Iframe.IFRAME_MAIN` | Main content iframe patterns (3 variants) |
| **Loaders** | `NewUI.Common.Loader.LOADER_DIVS` | Loading div patterns (1 variant) |
| **Loading Indicators** | `NewUI.Common.Loader.LOADING_INDICATORS` | Loading text/spinners (4 variants) |
| **Popup Close** | `NewUI.Common.Popup.CLOSE_BUTTONS` | Popup/tour close buttons (8 variants) |
| **Reports Menu** | `NewUI.Navigation.Menu.REPORTS_MENU` | Main reports menu item (5 variants) |
| **Export Button** | `NewUI.Export.Button.EXPORT_BUTTON` | Vessel export button (3 variants) |
| **Excel Menu** | `NewUI.Export.Menu.EXCEL_MENU_ITEM` | Excel export menu (5 variants) |
| **Excel All** | `NewUI.Export.Menu.EXCEL_ALL_OPTION` | Export all to Excel (5 variants) |
| **Barrel Details Menu** | `NewUI.Export.Menu.BARREL_DETAILS_MENU_ITEM` | Barrel details menu (3 variants) |
| **Barrel Details All** | `NewUI.Export.Menu.BARREL_DETAILS_ALL_OPTION` | Export all barrel details (3 variants) |
| **Generate Button** | `NewUI.Reports.Control.GENERATE_BUTTON` | Report generate button (4 variants) |
| **Vintage/Harvest Tab** | `NewUI.Reports.Category.VINTAGE_HARVEST_TAB` | Report category tab (5 variants) |

## 💡 Common Patterns

### Pattern 1: Simple Selector Access
```python
from Selectors import NewUI

# Get first (primary) selector
iframe = NewUI.Common.Iframe.IFRAME_MAIN[0]

# Try all variants
for selector in NewUI.Common.Iframe.IFRAME_MAIN:
    try:
        element = await page.locator(selector).wait_for(timeout=1000)
        break
    except:
        continue
```

### Pattern 2: With Performance Tracking
```python
from Selectors import NewUI, track_selector_attempt
import time

for selector in NewUI.Export.Button.EXPORT_BUTTON:
    start = time.time()
    try:
        await page.locator(selector).wait_for(timeout=1000)
        track_selector_attempt("export_button", selector, True, 
                              (time.time() - start) * 1000)
        break
    except:
        track_selector_attempt("export_button", selector, False,
                              (time.time() - start) * 1000)
```

### Pattern 3: Performance-Optimized
```python
from Selectors import get_prioritized_selectors

# Get selectors ordered by past performance
selectors = get_prioritized_selectors("export_button", ui_version="new")
for selector in selectors:
    try:
        await page.locator(selector).wait_for(timeout=1000)
        break
    except:
        continue
```

### Pattern 4: Helper Function
```python
from Selectors import NewUI, track_selector_attempt
import time

async def find_with_tracking(page, category, selectors, timeout=5000):
    """Try selectors and track performance"""
    for selector in selectors:
        start = time.time()
        try:
            locator = page.locator(selector)
            await locator.wait_for(timeout=timeout)
            elapsed = (time.time() - start) * 1000
            track_selector_attempt(category, selector, True, elapsed)
            return locator
        except:
            elapsed = (time.time() - start) * 1000
            track_selector_attempt(category, selector, False, elapsed)
    return None

# Usage
export_btn = await find_with_tracking(
    page, "export_button", 
    NewUI.Export.Button.EXPORT_BUTTON
)
```

## 📊 Tracking & Reporting

```python
from Selectors import (
    track_selector_attempt,
    get_best_selectors,
    export_stats_report
)

# Track an attempt
track_selector_attempt(
    category="export_button",
    selector="button#exportBtn",
    success=True,
    time_ms=125.5,
    context="vessels_page"
)

# Get top 3 performers
best = get_best_selectors("export_button", limit=3)

# Generate report
report = export_stats_report("performance_report.txt")
```

## 🔧 Utility Functions

```python
from Selectors import (
    validate_selector_format,
    get_selector_type,
    merge_selector_lists
)

# Validate
if validate_selector_format(my_selector):
    print("Valid!")

# Detect type
type = get_selector_type("button#btn")  # Returns 'css'
type = get_selector_type("//button")    # Returns 'xpath'
type = get_selector_type("text=Click")  # Returns 'text'

# Merge lists
merged = merge_selector_lists(list1, list2, list3)
```

## 🔄 Migration from Old System

```python
# Old way (still works!)
from tools.vintrace_selectors import NewUISelectors
iframe = NewUISelectors.IFRAME_MAIN

# New way (recommended)
from Selectors import NewUI
iframe = NewUI.Common.Iframe.IFRAME_MAIN

# Both produce identical results
```

## 🎯 Best Practices

1. **Always track performance** - Build data for optimization
2. **Use prioritized selectors** - Let data guide selector order
3. **Add context** - Track where selectors are used
4. **Validate before use** - Catch malformed selectors early
5. **Generate reports** - Review performance regularly

## 📁 File Locations

| Purpose | Location |
|---------|----------|
| Main package | `Selectors/__init__.py` |
| New UI selectors | `Selectors/new_ui/*.py` |
| Tracking system | `Selectors/tracking/selector_performance.py` |
| Utilities | `Selectors/utils.py` |
| Documentation | `Selectors/README.md` |
| Demo script | `Selectors/demo.py` |
| Tests | `Selectors/test_selectors.py` |
| Integration example | `Selectors/example_integration.py` |
| Performance data | `Selectors/tracking/selector_stats.json` (auto-generated) |

## 🆘 Troubleshooting

**Problem: ModuleNotFoundError: No module named 'Selectors'**
```python
# Solution: Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**Problem: Selectors not found on page**
```python
# Solution: Try all variants and track results
for selector in selectors:
    try:
        await page.locator(selector).wait_for(timeout=1000)
        break
    except:
        continue
```

**Problem: Want to see performance data**
```python
# Solution: Generate a report
from Selectors import export_stats_report
print(export_stats_report())
```

## 📚 Full Documentation

See `Selectors/README.md` for complete documentation.
