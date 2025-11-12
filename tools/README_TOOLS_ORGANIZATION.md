# Tools Directory Organization

This document explains the organization and purpose of scripts in the `tools/` directory.

## Directory Structure

- `tools/` - Main tools directory (149 Python files)
- `tools/BI/` - Business Intelligence orchestration scripts
- `tools/bit/` - Trading/financial scripts (backtrader strategies)
- `tools/models/` - Data models
- `tools/utils/` - Utility functions
- `tools/seed/` - Database seeding scripts
- `tools/SQL/` - SQL scripts
- `tools/PostgreSQL/` - PostgreSQL-specific scripts

## Data Storage Convention

**All scripts save data to `Main/data/` subdirectories**, which is included in `.gitignore` to prevent committing large data files.

Example paths:
- `Main/data/GET--vessels/` - Vessel data
- `Main/data/GET--blocks/` - Block data
- `Main/data/GET--shipments/` - Shipment data
- `Main/data/GET--intakes/` - Intake data
- `Main/data/id_tables/` - ID lookup tables
- `Main/data/vintrace_reports/` - Vintrace report outputs

## Script Categories

### 1. Data Fetching Scripts (API)
Fetch data from Vintrace API and save to `Main/data/`:

- `fetch_Vessels*.py` - Vessel data (multiple variants for different needs)
- `fetch_blocks*.py` - Block data
- `fetch_shipments*.py` - Shipment data
- `fetch_transactions*.py` - Transaction data
- `fetch_fruit_intakes*.py` - Fruit intake data
- `fetch_workorders*.py` - Work order data
- `fetch_barrels.py` - Barrel data
- `fetch_costs.py` - Cost data
- `fetch_samples_lims.py` - LIMS sample data

### 2. Data Upload Scripts (to SQL Server)
Upload data from JSON files to SQL Server:

- `upload_blocks.py` - Upload blocks
- `upload_vessels*.py` - Upload vessels
- `upload_shipments*.py` - Upload shipments
- `upload_transactions*.py` - Upload transactions
- `upload_intakes*.py` - Upload intakes
- `upload_fruit_intakes*.py` - Upload fruit intakes
- `upload_workorders*.py` - Upload work orders
- `upload_cost_movements*.py` - Upload cost movements
- `upload_bulk_intakes*.py` - Upload bulk intakes

### 3. Vintrace Playwright/Selenium Reports
Scrape reports from Vintrace web interface using browser automation:

- `vintrace_Bulk_Stock_Report*.py` - Bulk stock reports
- `vintrace_Grape_Report*.py` - Grape delivery reports
- `vintrace_playwright_Barrel_Report.py` - Barrel reports
- `vintrace_playwright_dispatch_search_console*.py` - Dispatch console data
- `vintrace_playwright_vessels_report.py` - Vessels report
- `vintrace_playwright_work_detailz.py` - Work detail reports
- `vintrace_playwright_analysis_report.py` - Analysis reports

### 4. Data Processing Scripts
Transform and process data:

- `tanks_to_json.py` - Convert tank data to JSON
- `melt_vessels.py` - Transform vessel data
- `special_table_linker.py` - Link special transfer tables
- `bulk_intake_consolidate.py` - Consolidate bulk intakes
- `export_shipments_flat_excel.py` - Export flat shipment data
- `vintrace_work_detail_extract_parcel_weightag_glob*.py` - Extract parcel weight data

### 4a. Analysis Scripts
Advanced analytics and reporting:

- `vessel_batch_lineage_analysis.py` - **NEW** - Analyze vessel-batch transaction lineage
  - Tracks gallons flow through batch transactions
  - Creates complete lineage maps showing all contributing batches
  - Exports Power BI ready CSV files
  - See `VESSEL_BATCH_LINEAGE_README.md` for full documentation
  - Example usage: `tools/examples/vessel_batch_lineage_examples.py`

### 5. Orchestration Scripts
Run multiple scripts in sequence:

- `looper_dooper_data.py` - Main data fetching orchestrator (30min intervals)
- `looper_dooper_BI.py` - BI reports orchestrator
- `looper_dooper_BI_bottle.py` - Bottling-specific BI orchestrator
- `BI/Main.py` - BI module orchestrator

### 6. Utility Scripts
Helper and testing scripts:

- `test_conn.py` - Test database connection
- `test_post_one.py` - Test POST endpoint
- `test_fetch_one_shipment.py` - Test shipment fetch
- `vintrace_helpers.py` - Shared helper functions
- `export_ad_users.py` - Export Active Directory users

## Version-Numbered Files

### Work Orders (v6 vs v7)
The Vintrace API has different versions for work orders:

**v6 Work Orders:**
- `fetch_wo_v6.py` - Full v6 work order fetch with logging
- `fetch_wo_v6_simple.py` - Simplified v6 fetch
- `fetch_wo_v6_simple_raw.py` - Raw v6 fetch
- `fetch_workorders_v6_singley.py` - **ACTIVE** - Used by loopers for v6 data

**v7 Work Orders:**
- `fetch_workorders_v7.py` - **ACTIVE** - Main v7 work order fetch (used by loopers)
- `fetch_workorders_v7_extraction.py` - Extract specific v7 data
- `fetch_workorders_v7_extra_with_v6_fetch.py` - Fetch v7 with additional v6 data
- `fetch_workorders_v7_with_v7_jobs.py` - Fetch v7 work orders with job details

**Combination Scripts:**
- `fetch_workorders_v7_v6_WO_combine_jsons.py` - Combine v6 and v7 JSON files
- `fetch_workorders_v7_v6_WO_combine_jsons_2025.py` - **ACTIVE** - Enhanced combination (used by loopers)

### Transactions (v2)
- `upload_transactions_main.py` - Original transaction upload
- `upload_transactions_main_v2.py` - Enhanced version with improvements
- `upload_transactions_main_v2_sandbox.py` - Sandbox testing version

### Work Detail Extraction (v2)
- `vintrace_work_detail_extract_parcel_weightag_glob_convert_v2.py` - Main v2 extraction
- `vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_Disp.py` - Dispatch variant
- `vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_onHand.py` - On-hand variant

## Files with Multiple Variants

### Vessels
Different levels of detail and purposes:
- `fetch_Vessels.py` - Full vessel data with barrel groups
- `fetch_Vessels_thin.py` - Minimal vessel data (faster)
- `fetch_Vessels_allo.py` - Vessel allocation data
- `fetch_Vessels_liveMetrics.py` - Real-time metrics
- `fetch_Vessels_with_all_barrels.py` - Comprehensive barrel information

### Shipments
- `fetch_shipments.py` - Full shipment fetch
- `fetch_shipments_10.py` - Fetch 10 sample shipments
- `fetch_shipments_thin.py` - Minimal shipment data
- `upload_shipments.py` - Main upload with chunking
- `upload_shipments_main.py` - Alternative main upload
- `upload_shipments_short.py` - Short version
- `upload_shipments_flat.py` - Flat structure upload

### Dispatch Console
- `vintrace_playwright_dispatch_search_console.py` - Main dispatch console scraper
- `vintrace_playwright_dispatch_search_console2.py` - Alternative version
- `vintrace_playwright_dispatch_search_console_main.py` - Main orchestrator
- `vintrace_playwright_dispatch_search_console_recent_7.py` - Recent 7 days
- `vintrace_playwright_dispatch_search_console_missing.py` - Missing dispatches
- `vintrace_playwright_dispatch_search_console_fix_partials.py` - Fix partial records

## Actively Used Scripts (Referenced in Loopers)

From `looper_dooper_data.py`:
- `fetch_fruit_intakes.py`
- `upload_fruit_intakes_main.py`
- `vintrace_Grape_Report_with_bookingSummary_playwright.py`
- `vintrace_grape_report_detail.py`
- `fetch_workorders_v7.py`
- `upload_workorders_v7.py`
- `fetch_workorders_v6_singley.py`
- `fetch_workorders_v7_v6_WO_combine_jsons_2025.py`
- `vintrace_work_detail_extract_parcel_weightag_glob.py`
- `vintrace_playwright_dispatch_search_console_recent_7.py`
- `vintrace_playwright_dispatch_search_console_missing.py`
- `vintrace_playwright_dispatch_search_console_fix_partials.py`
- `vintrace_search_console_data.py`
- `vintrace_playwright_work_detailz.py`
- `vintrace_work_detail_extract_parcel_weightag_glob_convert_v2.py`
- `vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_Disp.py`
- `vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_onHand.py`

## Recent Cleanup (2025-11-12)

### Removed Duplicate Files
The following duplicate " copy" files were removed as they were outdated versions:
- `job_GET_copy.py` - Contained hardcoded credentials (security issue)
- `vintrace_Grape_Report copy.py` - Exact duplicate
- `upload_shipments copy.py` - Old version without chunking
- `upload_transactions_main_up copy.py` - Old version
- `webdriver_agcode_harvestloads_copy.py` - Old version
- `vintrace_Bulk_Stock_Report_playwright copy.py` - Old version
- `vintrace_Bulk_Stock_Report_playwright_disp copy.py` - Old version
- `vintrace_playwright_dispatch_search_console copy.py` - Old version

### Updated Files
- `export_ad_users.py` - Now saves to `Main/data/ad_users.csv` (was saving to current directory)

## Recommendations for Future Cleanup

1. **Unused v6 variants** - Consider archiving:
   - `fetch_wo_v6.py`
   - `fetch_wo_v6_simple.py`
   - `fetch_wo_v6_simple_raw.py`
   
2. **Test files** - Consider moving to a dedicated `tests/` directory:
   - `test_conn.py`
   - `test_post_one.py`
   - `test_fetch_one_shipment.py`
   - `mongo_test.py`
   - All `*_test.py` files

3. **BI duplicates** - Some files in `tools/BI/` are identical to `tools/`:
   - Consider using imports/symlinks instead of duplicates
   - Or clearly document which is the source of truth

## Usage Examples

See README.md for Docker commands. Common patterns:

```bash
# Fetch data from API
python tools/fetch_Vessels.py

# Upload to SQL Server
docker-compose exec api bash
export PYTHONPATH=/app
python tools/upload_vessels_up.py

# Run orchestrator
python tools/looper_dooper_data.py
```
