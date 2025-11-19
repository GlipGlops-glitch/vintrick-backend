# Quick Start: Using the Refactored Analysis Report

## Prerequisites
- Python 3.7+
- Playwright installed (`pip install playwright && playwright install`)
- `.env` file with Vintrace credentials

## .env Setup
Create a `.env` file in the project root:
```bash
VINTRACE_USER=your_email@example.com
VINTRACE_PW=your_password
```

## Usage Examples

### 1. Standalone Script (Easiest)
```bash
cd /path/to/vintrick-backend
python ReportsVintrace/old_ui/run_analysis_report.py
```

### 2. Import and Use (Programmatic)
```python
import asyncio
from ReportsVintrace.old_ui.analysis_report import AnalysisReport

async def main():
    # Use context manager for automatic cleanup
    async with AnalysisReport(headless=False) as report:
        # Step 1: Login
        print("Logging in...")
        success = await report.login()
        if not success:
            print("Login failed!")
            return
        
        # Step 2: Download report
        print("Downloading report...")
        success = await report.download(
            start_date="08/01/2025",    # MM/DD/YYYY format
            end_date=None,               # None = today
            show_active_only=True,       # Filter active only
            output_filename="Vintrace_analysis_export.csv"
        )
        
        if success:
            print("✅ Report downloaded successfully!")
        else:
            print("❌ Download failed")

# Run it
asyncio.run(main())
```

### 3. Custom Date Range
```python
async with AnalysisReport(headless=False) as report:
    await report.login()
    
    # Custom date range
    await report.download(
        start_date="01/01/2025",
        end_date="12/31/2025",
        show_active_only=True
    )
```

### 4. Headless Mode (Background)
```python
# Run without opening browser window
async with AnalysisReport(headless=True) as report:
    await report.login()
    await report.download()
```

### 5. Custom Download Directory
```python
async with AnalysisReport(
    headless=False,
    download_dir="custom/path/to/reports/"
) as report:
    await report.login()
    await report.download(
        output_filename="my_custom_name.csv"
    )
```

## Output

**Default Location:**
```
Main/data/vintrace_reports/analysis/Vintrace_analysis_export.csv
```

**Debug Screenshots (on error):**
```
debug_screenshots/debug_<error_type>_<timestamp>.png
```

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'playwright'"
**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Issue: "VINTRACE_USER or VINTRACE_PW environment variables not set"
**Solution:** Create a `.env` file with your credentials (see above)

### Issue: Download fails
**Check:**
1. Debug screenshots in `debug_screenshots/` folder
2. Ensure you have write permissions to download directory
3. Check network connectivity to Vintrace

## Advanced Usage

### View Selector Performance
```python
from Selectors.tracking import get_best_selectors, export_stats_report

# Get best performing selectors
best = get_best_selectors("generate_button", limit=5)
for selector_info in best:
    print(f"{selector_info['selector']} - {selector_info['success_rate']:.1%}")

# Export full report
report = export_stats_report("selector_performance.txt")
print(report)
```

### Error Handling
```python
async with AnalysisReport(headless=False) as report:
    try:
        await report.login()
        success = await report.download()
        
        if not success:
            print("Download failed, check debug screenshots")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
```

### Multiple Reports in Sequence
```python
async def download_multiple():
    async with AnalysisReport(headless=False) as report:
        await report.login()  # Login once
        
        # Download for different date ranges
        for month in range(1, 13):
            start = f"{month:02d}/01/2025"
            end = f"{month:02d}/28/2025"
            
            await report.download(
                start_date=start,
                end_date=end,
                output_filename=f"analysis_{month:02d}_2025.csv"
            )

asyncio.run(download_multiple())
```

## Integration with Existing Code

### Replace Old Import
**Before:**
```python
# Don't use this anymore
from tools.vintrace_playwright_analysis_report import download_analysis_report
```

**After:**
```python
from ReportsVintrace.old_ui.analysis_report import AnalysisReport

async def my_function():
    async with AnalysisReport() as report:
        await report.login()
        await report.download()
```

## Validation

Test that everything is set up correctly:
```bash
cd /path/to/vintrick-backend
python test_analysis_refactor.py
```

Expected output:
```
============================================================
VALIDATING REFACTORED ANALYSIS REPORT STRUCTURE
============================================================
...
✅ ALL VALIDATION TESTS PASSED!
============================================================
```

## Next Steps

1. ✅ Run the validation test
2. ✅ Set up your `.env` file
3. ✅ Try the standalone script first
4. ✅ Explore the programmatic API
5. ✅ Check `ReportsVintrace/README.md` for full documentation

## Getting Help

- **Documentation:** See `ReportsVintrace/README.md`
- **Migration Guide:** See `ANALYSIS_REPORT_MIGRATION.md`
- **Selector Reference:** See `Selectors/README.md`
- **Example Code:** See `ReportsVintrace/old_ui/run_analysis_report.py`

## What's Different from the Old Script?

| Feature | Old Script | New System |
|---------|-----------|------------|
| **Run Command** | `python tools/vintrace_playwright_analysis_report.py` | `python ReportsVintrace/old_ui/run_analysis_report.py` |
| **Import** | Not importable | `from ReportsVintrace.old_ui.analysis_report import AnalysisReport` |
| **Configuration** | Hardcoded | Configurable via parameters |
| **Selectors** | Scattered in code | Organized in `Selectors/old_ui/` |
| **Tracking** | None | Automatic performance tracking |
| **Reusability** | Copy/paste | Inherit from base class |

**Bottom Line:** Same functionality, better organization, more features! 🎉
