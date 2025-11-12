# Quick Reference: Which Script to Use When

This guide helps you choose the right script for common tasks.

## Fetching Data from Vintrace API

### Vessels
- **Full data with barrel groups**: `fetch_Vessels.py`
- **Quick/minimal data**: `fetch_Vessels_thin.py`
- **Allocation data**: `fetch_Vessels_allo.py`
- **Live metrics**: `fetch_Vessels_liveMetrics.py`
- **All barrel details**: `fetch_Vessels_with_all_barrels.py`

### Shipments
- **Full shipment data**: `fetch_shipments.py`
- **Sample (10 records)**: `fetch_shipments_10.py`
- **Minimal data**: `fetch_shipments_thin.py`

### Work Orders
- **Current v7 API**: `fetch_workorders_v7.py` ⭐ RECOMMENDED
- **Legacy v6 API**: `fetch_workorders_v6_singley.py`
- **Combined v6+v7 data**: `fetch_workorders_v7_v6_WO_combine_jsons_2025.py`
- **With job details**: `fetch_workorders_v7_with_v7_jobs.py`

### Transactions
- **Main fetch**: `fetch_transactions.py`
- **With hard dates**: `fetch_transactions_hard_dates.py`
- **Sandbox testing**: `fetch_transactions_sandbox.py`

### Fruit Intakes
- **All intakes**: `fetch_fruit_intakes_all.py`
- **Current season**: `fetch_fruit_intakes_current.py`
- **Main fetch**: `fetch_fruit_intakes.py`

### Other Data
- **Blocks**: `fetch_blocks.py`
- **Barrels**: `fetch_barrels.py`
- **Costs**: `fetch_costs.py`
- **LIMS samples**: `fetch_samples_lims.py`

## Uploading Data to SQL Server

### Inside Docker Container
Always run these commands inside the Docker container:
```bash
docker-compose exec api bash
export PYTHONPATH=/app
python tools/[script_name]
```

### Vessels
- **Main upload**: `upload_vessels_up.py`

### Shipments
- **Full upload**: `upload_shipments_main_up.py` ⭐ RECOMMENDED (from README)
- **Quick/test upload**: `upload_shipments_short_up.py`
- **Flat structure**: `upload_shipments_flat.py`

### Transactions
- **Main upload**: `upload_transactions_main_up.py` ⭐ RECOMMENDED (from README)
- **Test version**: `upload_transactions_main_up_test.py`
- **Summary only**: `upload_transactions_main_summary.py`

### Work Orders
- **v7 upload**: `upload_workorders_v7.py`

### Intakes
- **Bulk intakes**: `upload_bulk_intakes_main.py`
- **Fruit intakes**: `upload_fruit_intakes_main.py`
- **Main upload**: `upload_intakes_up.py`

### Other
- **Blocks**: `upload_blocks.py`
- **Cost movements**: `upload_cost_movements_main.py`
- **ID tables**: `upload_id_tables_main.py`

## Scraping Vintrace Web Reports (Playwright/Selenium)

### Stock Reports
- **Bulk stock**: `vintrace_Bulk_Stock_Report_playwright.py`
- **Dispatch variant**: `vintrace_Bulk_Stock_Report_playwright_disp.py`

### Grape/Fruit Reports
- **With booking summary**: `vintrace_Grape_Report_with_bookingSummary_playwright.py`
- **Detail extraction**: `vintrace_grape_report_detail.py`

### Dispatch Console
- **Recent 7 days**: `vintrace_playwright_dispatch_search_console_recent_7.py`
- **Missing dispatches**: `vintrace_playwright_dispatch_search_console_missing.py`
- **Fix partials**: `vintrace_playwright_dispatch_search_console_fix_partials.py`

### Analysis & Detail Reports
- **Barrel report**: `vintrace_playwright_Barrel_Report.py`
- **Vessels report**: `vintrace_playwright_vessels_report.py`
- **Work details**: `vintrace_playwright_work_detailz.py`
- **Analysis report**: `vintrace_playwright_analysis_report.py`

## Data Processing & Transformation

### Vessel Data
- **Melt/transform**: `melt_vessels.py`

### Work Detail Extraction
- **Main v2**: `vintrace_work_detail_extract_parcel_weightag_glob_convert_v2.py`
- **Dispatch variant**: `vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_Disp.py`
- **On-hand variant**: `vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_onHand.py`

### Other
- **Tank data**: `tanks_to_json.py`
- **Link transfers**: `special_table_linker.py`
- **Consolidate intakes**: `bulk_intake_consolidate.py`
- **Export shipments**: `export_shipments_flat_excel.py`

## Running Multiple Scripts (Orchestrators)

### Continuous Data Updates
- **Main orchestrator**: `looper_dooper_data.py` (30-minute intervals)
- **BI reports**: `looper_dooper_BI.py`
- **Bottling BI**: `looper_dooper_BI_bottle.py`
- **BI module**: `BI/Main.py`

## Testing & Utilities

### Connection Tests
- **Database**: `test_conn.py`
- **API POST**: `test_post_one.py`
- **Shipment fetch**: `test_fetch_one_shipment.py`

### Other Utilities
- **Export AD users**: `export_ad_users.py`
- **Helper functions**: `vintrace_helpers.py`

## Common Workflows

### 1. Full Data Refresh
```bash
# Start orchestrator (runs continuously)
python tools/looper_dooper_data.py
```

### 2. Manual Data Fetch & Upload
```bash
# Fetch from API
python tools/fetch_Vessels.py
python tools/fetch_shipments.py

# Upload to SQL (in Docker)
docker-compose exec api bash
export PYTHONPATH=/app
python tools/upload_vessels_up.py
python tools/upload_shipments_main_up.py
```

### 3. BI Report Generation
```bash
# Run BI orchestrator
python tools/BI/Main.py
```

### 4. Quick Test
```bash
# Fetch sample data
python tools/fetch_shipments_10.py

# Upload test data
docker-compose exec api bash
export PYTHONPATH=/app
python tools/upload_shipments_short_up.py
```

## File Naming Conventions

- `fetch_*.py` - Fetches data from Vintrace API
- `upload_*.py` - Uploads data to SQL Server
- `vintrace_*.py` - Scrapes Vintrace web interface
- `*_main.py` - Main/primary version of a script
- `*_up.py` - Upload version (often with chunking/batching)
- `*_thin.py` - Minimal/lightweight version
- `*_short.py` - Sample/subset version
- `*_v6.py`, `*_v7.py` - API version specific
- `looper_*.py` - Continuous orchestration scripts

## Output Locations

All scripts save data to `Main/data/` subdirectories:
- `Main/data/GET--vessels/` - Vessel JSON files
- `Main/data/GET--shipments/` - Shipment JSON files
- `Main/data/GET--blocks/` - Block JSON files
- `Main/data/GET--intakes/` - Intake JSON files
- `Main/data/GET--jobs/` - Job/work order JSON files
- `Main/data/id_tables/` - ID lookup tables
- `Main/data/vintrace_reports/` - Scraped report data

Note: `Main/` is in `.gitignore` and won't be committed to the repository.

## Need Help?

1. Check the script header comments for usage instructions
2. See `README_TOOLS_ORGANIZATION.md` for detailed documentation
3. See main `README.md` for Docker and environment setup
