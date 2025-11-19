# Vintrace Selector Management System

A clean, comprehensive system for managing Vintrace UI selectors with performance tracking and intelligent prioritization.

## 📁 Architecture

```
Selectors/
├── __init__.py                    # Main package exports
├── README.md                      # This file
├── utils.py                       # Helper functions
├── new_ui/                        # New UI (PrimeFaces) selectors
│   ├── __init__.py
│   ├── common.py                  # Iframes, loaders, popups
│   ├── navigation.py              # Menus, tabs, navigation
│   ├── reports.py                 # Report configuration & generation
│   ├── vessels.py                 # Vessel/barrel pages
│   └── export.py                  # Export & download functionality
└── tracking/                      # Performance tracking system
    ├── __init__.py
    ├── selector_performance.py    # Track selector success rates
    └── selector_stats.json        # Performance data (auto-generated)
```

## 🚀 Quick Start

### Basic Usage

```python
# Import the selector system
from Selectors import NewUI

# Access selectors by category
iframe_selectors = NewUI.Common.Iframe.IFRAME_MAIN
export_button = NewUI.Export.Button.EXPORT_BUTTON
reports_menu = NewUI.Navigation.Menu.REPORTS_MENU

# Use with Playwright
await page.locator(iframe_selectors[0]).wait_for()
```

### With Performance Tracking

```python
from Selectors import NewUI, track_selector_attempt
import time

# Try selectors and track performance
for selector in NewUI.Export.Button.EXPORT_BUTTON:
    start = time.time()
    try:
        element = await page.locator(selector).wait_for(timeout=1000)
        time_ms = (time.time() - start) * 1000
        track_selector_attempt(
            category="export_button",
            selector=selector,
            success=True,
            time_ms=time_ms,
            context="vessels_page"
        )
        break
    except:
        time_ms = (time.time() - start) * 1000
        track_selector_attempt(
            category="export_button",
            selector=selector,
            success=False,
            time_ms=time_ms,
            context="vessels_page"
        )
```

### Get Best Performing Selectors

```python
from Selectors import get_best_selectors, get_prioritized_selectors

# Get top 3 performers for a category
best = get_best_selectors("export_button", limit=3)
for selector_info in best:
    print(f"Selector: {selector_info['selector']}")
    print(f"Success Rate: {selector_info['success_rate']:.1%}")
    print(f"Avg Time: {selector_info['avg_time_ms']:.2f}ms")

# Get selectors automatically ordered by performance
selectors = get_prioritized_selectors("export_button", ui_version="new")
```

### Generate Performance Report

```python
from Selectors import export_stats_report

# Generate and save a report
report = export_stats_report(output_file="selector_performance_report.txt")
print(report)
```

## 📚 Selector Categories

### Common Elements (`NewUI.Common`)

**Iframes** - `NewUI.Common.Iframe`
- `IFRAME_MAIN` - Main content iframe patterns

**Loaders** - `NewUI.Common.Loader`
- `LOADER_DIVS` - Loading div patterns
- `LOADING_INDICATORS` - Various loading indicators

**Popups** - `NewUI.Common.Popup`
- `CLOSE_BUTTONS` - Popup close buttons

### Navigation (`NewUI.Navigation`)

**Menus** - `NewUI.Navigation.Menu`
- `REPORTS_MENU` - Reports menu item

**Tabs** - `NewUI.Navigation.Tab`
- Tab selectors (to be expanded)

### Export Functionality (`NewUI.Export`)

**Buttons** - `NewUI.Export.Button`
- `EXPORT_BUTTON` - Main export button

**Menus** - `NewUI.Export.Menu`
- `EXCEL_MENU_ITEM` - Excel export option
- `EXCEL_ALL_OPTION` - Export all to Excel
- `BARREL_DETAILS_MENU_ITEM` - Barrel details option
- `BARREL_DETAILS_ALL_OPTION` - Export all barrel details

### Reports (`NewUI.Reports`)

**Categories** - `NewUI.Reports.Category`
- `VINTAGE_HARVEST_TAB` - Vintage/Harvest category
- `PRODUCT_ANALYSIS_CATEGORY` - Product Analysis category

**Controls** - `NewUI.Reports.Control`
- `GENERATE_BUTTON` - Report generation button
- `SHOW_ACTIVE_ONLY` - Active only checkbox
- `REPORT_STRIP` - Report container

**Format** - `NewUI.Reports.Format`
- `FORMAT_DROPDOWN` - Format selection dropdown

### Vessels (`NewUI.Vessels`)

**Tables** - `NewUI.Vessels.Table`
- Vessel table selectors (to be expanded)

## 🔧 Utility Functions

### `get_selector_list(module, attribute_name)`
Extract a selector list from a module/class.

```python
from Selectors import get_selector_list, NewUI

selectors = get_selector_list(NewUI.Common.Iframe, 'IFRAME_MAIN')
```

### `get_prioritized_selectors(category, ui_version='new')`
Get selectors ordered by performance metrics.

```python
from Selectors import get_prioritized_selectors

# Returns selectors ordered by success rate and speed
selectors = get_prioritized_selectors('export_button', ui_version='new')
```

### `validate_selector_format(selector)`
Validate a selector string for basic syntax correctness.

```python
from Selectors import validate_selector_format

if validate_selector_format("button#myBtn"):
    print("Valid selector!")
```

### `merge_selector_lists(*lists)`
Intelligently merge multiple selector lists, removing duplicates.

```python
from Selectors import merge_selector_lists

list1 = ["a", "b", "c"]
list2 = ["b", "c", "d"]
merged = merge_selector_lists(list1, list2)  # ['a', 'b', 'c', 'd']
```

### `get_selector_type(selector)`
Determine the type of a selector (css, xpath, text, role).

```python
from Selectors import get_selector_type

type1 = get_selector_type("button#myBtn")  # 'css'
type2 = get_selector_type("//button[@id='myBtn']")  # 'xpath'
type3 = get_selector_type("text=Click me")  # 'text'
```

## 📊 Performance Tracking

The tracking system automatically records:
- Success/failure of each selector attempt
- Time taken to find elements (milliseconds)
- Context information (page, UI state)
- Success rates and averages

### Tracking Methods

```python
from Selectors.tracking import (
    track_selector_attempt,
    get_best_selectors,
    get_selector_stats,
    export_stats_report
)

# Track an attempt
track_selector_attempt(
    category="export_button",
    selector="button#vesselsForm\\:vesselsDT\\:exportButton",
    success=True,
    time_ms=125.5,
    context="vessels_page"
)

# Get best performers
best = get_best_selectors("export_button", limit=3)

# Get detailed stats
stats = get_selector_stats("export_button")

# Generate report
report = export_stats_report("performance_report.txt")
```

## 🎯 Best Practices

### 1. Always Track Performance

```python
# Track every selector attempt to build performance data
for selector in selectors:
    start = time.time()
    try:
        await page.locator(selector).wait_for(timeout=1000)
        track_selector_attempt(category, selector, True, elapsed_ms)
        break
    except:
        track_selector_attempt(category, selector, False, elapsed_ms)
```

### 2. Use Prioritized Selectors

```python
# Let the system order selectors by performance
selectors = get_prioritized_selectors("export_button")
# Fastest, most reliable selectors come first
```

### 3. Add Context

```python
# Context helps understand when selectors work best
track_selector_attempt(
    category="export_button",
    selector=sel,
    success=True,
    time_ms=100,
    context="vessels_page_after_filter"  # Specific context
)
```

### 4. Validate Before Use

```python
from Selectors import validate_selector_format

if validate_selector_format(my_selector):
    # Use selector
    pass
```

### 5. Regular Reports

```python
# Generate reports after automation runs
from Selectors import export_stats_report

export_stats_report("reports/selector_performance.txt")
```

## 🆕 Adding New Selectors

### 1. Choose the Right Module

- **Common elements** → `new_ui/common.py`
- **Navigation** → `new_ui/navigation.py`
- **Reports** → `new_ui/reports.py`
- **Vessels** → `new_ui/vessels.py`
- **Export** → `new_ui/export.py`

### 2. Add to Appropriate Class

```python
# In new_ui/export.py
class ExportButtonSelectors:
    NEW_BUTTON: List[str] = [
        "button#newBtn",  # Primary selector
        "button.new-btn-class",  # Fallback
    ]
```

### 3. Document Discovery Method

```python
# Discovery: Playwright codegen (2025-01-19)
# Note: Works best after page load completes
NEW_BUTTON: List[str] = [...]
```

### 4. Export in `__init__.py`

```python
# In new_ui/__init__.py
from .export import ExportButtonSelectors

class Export:
    Button = ExportButtonSelectors
```

### 5. Test and Track

```python
# Test the new selector
from Selectors import NewUI, track_selector_attempt

selector = NewUI.Export.Button.NEW_BUTTON[0]
# ... test and track performance ...
```

## 🔍 Selector Discovery Methods

Selectors in this system come from:

1. **Playwright Codegen** - Interactive recording (most reliable)
2. **HTML Analysis** - Examining saved HTML files
3. **Manual Testing** - Trial and error in live sessions
4. **Performance Data** - Learning from tracking metrics

Each selector includes comments about its discovery method and reliability.

## 🚨 Important Notes

### PrimeFaces ID Escaping

PrimeFaces uses colons (`:`) in IDs which must be escaped in CSS selectors:

```python
# Wrong
"button#vesselsForm:vesselsDT:exportButton"

# Correct (escaped)
"button#vesselsForm\\:vesselsDT\\:exportButton"

# Alternative (attribute selector)
"button[id='vesselsForm:vesselsDT:exportButton']"
```

### Selector Order Matters

Selectors are listed in priority order:
1. Most reliable (usually from codegen)
2. Fallback options
3. Generic patterns

### Thread Safety

The tracking system uses thread-safe JSON writes, making it safe to use in concurrent automation scripts.

## 📝 Migration from Old System

If you're migrating from `tools/vintrace_selectors.py`:

```python
# Old way
from tools.vintrace_selectors import NewUISelectors
iframe = NewUISelectors.IFRAME_MAIN

# New way
from Selectors import NewUI
iframe = NewUI.Common.Iframe.IFRAME_MAIN

# Both work! The old file still exists for backward compatibility
```

## 🤝 Contributing

When adding new selectors:
1. Test thoroughly
2. Document discovery method
3. Include context/notes
4. Track performance
5. Update this README if adding new categories

## 📜 Version History

- **1.0.0** (2025-01-19) - Initial release
  - Organized selector structure
  - Performance tracking system
  - Utility functions
  - Comprehensive documentation

## 👤 Author

GlipGlops-glitch

## 📄 License

Internal use for Vintrace automation.
