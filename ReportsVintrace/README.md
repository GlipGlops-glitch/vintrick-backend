# ReportsVintrace - Consolidated Vintrace Report Scripts

A clean, organized system for automating Vintrace report downloads using the Selectors system with performance tracking.

**Author:** GlipGlops-glitch  
**Created:** 2025-01-19

## 📁 Architecture

```
ReportsVintrace/
├── __init__.py
├── config.py              # Common configuration (timeouts, URLs)
├── README.md              # This file
├── common/                # Shared functionality
│   ├── __init__.py
│   ├── base_report.py     # Base classes (BaseReport, OldUIReport)
│   └── helpers.py         # Helper functions using Selectors
└── old_ui/                # Old UI reports
    ├── __init__.py
    ├── analysis_report.py # Product Analysis Report
    └── run_analysis_report.py # Standalone runner
```

## 🚀 Quick Start

### Analysis Report (Old UI)

Download the Product Analysis data export:

```python
import asyncio
from ReportsVintrace.old_ui.analysis_report import AnalysisReport

async def main():
    async with AnalysisReport(headless=False) as report:
        # Login to Vintrace
        await report.login()
        
        # Download the report
        success = await report.download(
            start_date="08/01/2025",
            show_active_only=True
        )
        
        if success:
            print("✅ Report downloaded!")

asyncio.run(main())
```

### Standalone Execution

```bash
# From project root
python ReportsVintrace/old_ui/run_analysis_report.py
```

## 📊 Available Reports

### Old UI Reports

#### Analysis Report (`AnalysisReport`)

Downloads Product Analysis data export CSV.

**Usage:**
```python
from ReportsVintrace.old_ui.analysis_report import AnalysisReport

async with AnalysisReport(headless=False) as report:
    await report.login()
    await report.download(
        start_date="08/01/2025",           # Start date (MM/DD/YYYY)
        end_date=None,                      # End date (default: today)
        show_active_only=True,              # Show only active products
        output_filename="Vintrace_analysis_export.csv"
    )
```

**Parameters:**
- `start_date` (str): Start date in MM/DD/YYYY format (default: `"08/01/2025"`)
- `end_date` (str, optional): End date in MM/DD/YYYY format (default: today's date)
- `show_active_only` (bool): Whether to filter for active products only (default: `True`)
- `output_filename` (str): Name for the downloaded file (default: `"Vintrace_analysis_export.csv"`)

**Output:**
- **Location:** `Main/data/vintrace_reports/analysis/`
- **Format:** CSV file
- **Contains:** Product analysis data for the specified date range

**Example Output File:**
```
Main/data/vintrace_reports/analysis/Vintrace_analysis_export.csv
```

## 🔧 Configuration

Configuration is centralized in `ReportsVintrace/config.py`:

```python
# Timeouts
DOWNLOAD_TIMEOUT = 1200000   # 20 minutes for large downloads
SELECTOR_TIMEOUT = 120000    # 2 minutes for selector waits
STANDARD_TIMEOUT = 30000     # 30 seconds

# URLs
LOGIN_URL = "https://auth.vintrace.app/sign-in?customerCode=smwe"
OLD_URL = "https://us61.vintrace.net/smwe/2.app?oldVintrace=true"

# Directories
DEFAULT_DOWNLOAD_DIR = "Main/data/vintrace_reports/"
DEBUG_SCREENSHOT_DIR = "debug_screenshots/"
```

## 🔑 Credentials

Reports require Vintrace credentials to be set in a `.env` file:

```bash
VINTRACE_USER=your_email@example.com
VINTRACE_PW=your_password
```

## 🎯 Features

### Selector System Integration

All reports use the centralized Selectors system:
- **Old UI Selectors:** `Selectors.old_ui.*`
- **Performance Tracking:** Automatic selector performance tracking
- **Intelligent Fallbacks:** Multiple selector options with automatic prioritization

### Performance Tracking

Every selector attempt is tracked:
```python
from Selectors.tracking import track_selector_attempt

track_selector_attempt(
    category="generate_button",
    selector="button:has-text('Generate')",
    success=True,
    time_ms=125.5,
    context="old_ui_reports"
)
```

### Error Handling

- **Debug Screenshots:** Automatic screenshots on failure
- **Detailed Logging:** Step-by-step progress logging
- **Graceful Fallbacks:** Multiple selector attempts before failing

### Base Classes

#### `BaseReport`
Abstract base class providing:
- Browser initialization
- Credential management
- Context manager support (`async with`)
- Abstract methods for `login()` and `download()`

#### `OldUIReport`
Extends `BaseReport` for Old UI:
- Pre-configured Old UI login
- Navigation to `oldVintrace=true` URL
- Ready to use for Old UI reports

## 📝 Date Format Specifications

All date inputs use **MM/DD/YYYY** format:
- ✅ Valid: `"08/01/2025"`, `"12/25/2024"`
- ❌ Invalid: `"2025-08-01"`, `"01-Aug-2025"`

## 🔍 Selector Categories

The Analysis Report uses these selector categories for tracking:

| Category | Purpose | Context |
|----------|---------|---------|
| `iframe_main` | Main content iframe | `old_ui_main_iframe` |
| `reports_icon` | Reports navigation icon | `old_ui_reports` |
| `product_analysis_category` | Product analysis menu | `old_ui_reports` |
| `report_strip` | Report container | `old_ui_reports_*` |
| `date_input` | Date field selectors | `old_ui_reports_from_date`, `old_ui_reports_to_date` |
| `show_active_checkbox` | Active only checkbox | `old_ui_reports` |
| `generate_button` | Generate/download button | `old_ui_reports` |

## 🛠️ Development

### Adding New Reports

1. **Create Report Class** in appropriate folder (`old_ui/` or `new_ui/`)
2. **Inherit from Base Class** (`OldUIReport` or `NewUIReport`)
3. **Implement Required Methods:**
   - `login()` (if custom login needed)
   - `download(**kwargs)`
4. **Use Selectors System:**
   ```python
   from Selectors.old_ui.reports import ReportsSelectors
   from Selectors.tracking import track_selector_attempt
   ```
5. **Add Performance Tracking** for all selector attempts
6. **Create Standalone Runner** (optional)
7. **Update Documentation** in this README

### Example New Report Template

```python
from ReportsVintrace.common.base_report import OldUIReport
from Selectors.old_ui.* import *
from Selectors.tracking import track_selector_attempt

class MyReport(OldUIReport):
    def __init__(self, headless: bool = False, download_dir: Optional[str] = None):
        super().__init__(headless=headless, download_dir=download_dir)
        self.download_dir = download_dir or "Main/data/vintrace_reports/my_report/"
        os.makedirs(self.download_dir, exist_ok=True)
    
    async def download(self, **kwargs) -> bool:
        # Implementation here
        pass
```

## 📦 Dependencies

- `playwright` - Browser automation
- `python-dotenv` - Environment variable management
- `asyncio` - Async/await support

## 🚨 Troubleshooting

### Login Issues
- Verify `.env` file contains correct credentials
- Check that `VINTRACE_USER` and `VINTRACE_PW` are set
- Ensure network connectivity to Vintrace

### Download Failures
- Check download directory permissions
- Verify sufficient disk space
- Review debug screenshots in `debug_screenshots/` folder

### Selector Issues
- Check `Selectors/tracking/selector_stats.json` for performance data
- Update selectors in `Selectors/old_ui/` if UI changed
- Add new selector variations if existing ones fail

## 📊 Performance Reports

Generate selector performance reports:

```python
from Selectors.tracking import export_stats_report

# Generate and save report
report = export_stats_report("selector_performance_report.txt")
print(report)
```

## 🔗 Related Documentation

- **Selectors System:** See `Selectors/README.md`
- **Selector Quick Reference:** See `Selectors/QUICK_REFERENCE.md`
- **Original Scripts:** See `tools/vintrace_*.py` (deprecated)

## 📜 Version History

- **1.0.0** (2025-01-19) - Initial release
  - Analysis Report (Old UI)
  - Base report classes
  - Helper functions with Selectors integration
  - Performance tracking system

## 👤 Author

GlipGlops-glitch

## 📄 License

Internal use for Vintrace automation.
