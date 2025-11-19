# ReportsVintrace

Consolidated, maintainable Vintrace report download scripts using the new Selectors system.

## Overview

This package provides standardized report downloaders for Vintrace winery software, with:
- ✅ Integration with the Selectors tracking system
- ✅ Base classes for consistency
- ✅ Type hints for better IDE support
- ✅ Async/await patterns
- ✅ Error handling and retry logic
- ✅ Debug screenshots
- ✅ Configurable download directories

## Structure

```
ReportsVintrace/
├── __init__.py
├── README.md (this file)
├── config.py                 # Configuration (timeouts, paths, etc.)
├── common/
│   ├── __init__.py
│   ├── base_report.py        # Base class for all reports
│   └── helpers.py            # Shared helper functions
├── current_ui/               # Reports using New UI
│   ├── __init__.py
│   ├── vessels_report.py     # Vessel details export
│   ├── barrel_report.py      # Barrel details export
│   ├── fruit_report.py       # Fruit/grape reports (TODO)
│   └── analysis_report.py    # Product analysis export (TODO)
├── old_ui/                   # Reports using Old UI
│   ├── __init__.py
│   └── analysis_report_legacy.py  # Legacy analysis report (TODO)
└── examples/
    ├── __init__.py
    └── example_usage.py      # Usage examples
```

## Quick Start

### Basic Usage

```python
import asyncio
from ReportsVintrace.current_ui.vessels_report import VesselsReport

async def main():
    async with VesselsReport(headless=False) as report:
        await report.login()  # Uses credentials from .env
        await report.download()

asyncio.run(main())
```

### Advanced Usage

```python
import asyncio
from ReportsVintrace.current_ui.vessels_report import VesselsReport
from ReportsVintrace.current_ui.barrel_report import BarrelReport

async def main():
    # Example 1: Custom download directory
    vessels = VesselsReport(
        headless=True,
        download_dir="my_custom_dir/"
    )
    async with vessels:
        await vessels.login()
        await vessels.download(output_filename="my_vessels.csv")
    
    # Example 2: Explicit credentials
    barrels = BarrelReport(headless=False)
    async with barrels:
        await barrels.login(
            username="user@example.com",
            password="password123"
        )
        await barrels.download()

asyncio.run(main())
```

## Available Reports

### Current UI (New UI)

#### VesselsReport
Downloads all vessel details as CSV.

```python
from ReportsVintrace.current_ui.vessels_report import VesselsReport

async with VesselsReport() as report:
    await report.login()
    await report.download(output_filename="vessels.csv")
```

**Default output:** `Main/data/vintrace_reports/vessel_details/Vintrace_all_vessels.csv`

#### BarrelReport
Downloads all barrel details as CSV.

```python
from ReportsVintrace.current_ui.barrel_report import BarrelReport

async with BarrelReport() as report:
    await report.login()
    await report.download(output_filename="barrels.csv")
```

**Default output:** `Main/data/vintrace_reports/barrel_details/Vintrace_all_barrels.csv`

### Old UI (Legacy)

Reports requiring the old Vintrace UI will be added here.

## Creating New Reports

To create a new report downloader:

1. **Inherit from the appropriate base class:**

```python
from ReportsVintrace.common.base_report import NewUIReport  # or OldUIReport

class MyCustomReport(NewUIReport):
    def __init__(self, headless=False, download_dir=None):
        super().__init__(
            headless=headless,
            download_dir=download_dir,
            report_type="custom"  # For default directory
        )
    
    async def download(self, **kwargs):
        # Implement your download logic here
        # Use self.iframe for interacting with the page
        # Use self.track_success() to log selector usage
        pass
```

2. **Use selectors from the Selectors package:**

```python
from Selectors.new_ui.export import ExportSelectors
from Selectors.tracking import track_selector_attempt

# In your download method:
for selector in ExportSelectors.EXPORT_BUTTON:
    try:
        element = await self.iframe.query_selector(selector)
        await element.click()
        track_selector_attempt(
            category="export_button",
            selector=selector,
            success=True,
            context="my_report"
        )
        break
    except Exception:
        track_selector_attempt(
            category="export_button",
            selector=selector,
            success=False,
            context="my_report"
        )
```

3. **Add standalone execution:**

```python
async def main():
    async with MyCustomReport() as report:
        await report.login()
        await report.download()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
VINTRACE_USER=your-email@example.com
VINTRACE_PW=your-password
```

### Default Settings

Modify `config.py` to change:
- Download directories
- Timeout values
- Browser settings
- URLs

```python
# In config.py
DEFAULT_DOWNLOAD_DIRS = {
    'vessels': 'Main/data/vintrace_reports/vessel_details/',
    'barrels': 'Main/data/vintrace_reports/barrel_details/',
    # ...
}

DOWNLOAD_TIMEOUT = 300_000  # 5 minutes
SELECTOR_TIMEOUT = 30_000   # 30 seconds
```

## Selectors System Integration

All reports use the centralized Selectors system:

- **Selectors/new_ui/** - Current UI selectors
- **Selectors/old_ui/** - Legacy UI selectors
- **Selectors/common.py** - Shared selectors (login, popups)
- **Selectors/tracking.py** - Selector performance tracking

The tracking system learns which selectors work best over time and saves data to `selector_tracking.json`.

## Error Handling

All reports include:
- Automatic retry with multiple selector variations
- Debug screenshots on failures (saved to `debug_screenshots/`)
- Detailed console logging
- Selector performance tracking

## Migration from Old Scripts

Old scripts in `tools/` and `tools/BI/` are being deprecated. To migrate:

| Old Script | New Report |
|------------|------------|
| `tools/BI/vintrace_playwright_vessels_report.py` | `ReportsVintrace.current_ui.vessels_report.VesselsReport` |
| `tools/BI/vintrace_playwright_Barrel_Report.py` | `ReportsVintrace.current_ui.barrel_report.BarrelReport` |
| `tools/BI/vintrace_playwright_fruit_report.py` | `ReportsVintrace.current_ui.fruit_report.FruitReport` (TODO) |
| `tools/BI/vintrace_playwright_analysis_report.py` | `ReportsVintrace.old_ui.analysis_report_legacy.AnalysisReportLegacy` (TODO) |

## Troubleshooting

### Login fails
- Check your `.env` file has correct credentials
- Ensure `VINTRACE_USER` and `VINTRACE_PW` are set

### Download times out
- Increase `DOWNLOAD_TIMEOUT` in `config.py`
- Check network connection

### Selectors not working
- Run in non-headless mode to debug: `VesselsReport(headless=False)`
- Check `selector_tracking.json` for selector performance
- Take screenshots with `await report.screenshot("debug_name")`

## Contributing

When adding new reports:
1. Follow the existing pattern (inherit from base class)
2. Use selectors from the Selectors package
3. Track all selector attempts
4. Add type hints
5. Include docstrings with examples
6. Add standalone execution support

## License

Internal use only - GlipGlops-glitch

## Author

GlipGlops-glitch
Created: 2025-01-19
