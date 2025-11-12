# python tools/looper_dooper_BI.py

import subprocess
import time

# List of Python scripts to run
python_scripts = [

    # # Fruit Intakes API
    # "tools/fetch_fruit_intakes.py",
    # "tools/upload_fruit_intakes_main.py",

#  API Fetches

    "tools/fetch_Vessels.py",
    # "tools/fetch_Vessels_allo.py",
    # "tools/fetch_Vessels_liveMetrics",

    "tools/melt_vessels.py",

    # Workorder Reports
    "tools/fetch_workorders_v7.py",
    "tools/upload_workorders_v7.py",
    "tools/fetch_workorders_v6_singley.py",
    "tools/fetch_workorders_v7_v6_WO_combine_jsons_2025.py",
    "tools/vintrace_work_detail_extract_parcel_weightag_glob.py",
    
#  Playwright Reports

    # Grape Delivery Report
    "tools/vintrace_Grape_Report_with_bookingSummary_playwright.py",
    "tools/vintrace_grape_report_detail.py",

    # Dispatch Console Reports
    "tools/vintrace_dispatch_search_console.py --mode recent --days 7",
    "tools/vintrace_dispatch_search_console.py --mode missing",
    "tools/vintrace_dispatch_search_console.py --mode fetch --csv path/to/missing_dispatches.csv",
    "tools/vintrace_search_console_data.py",

    # Work Detailz Reports
    "tools/vintrace_playwright_work_detailz.py",
    "tools/vintrace_work_detail_extract_parcel_weightag_glob_convert_v2.py",
    "tools/vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_Disp.py",
    "tools/vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_onHand.py",

    # All Barrels Report
    "tools/vintrace_playwright_Barrel_Report.py",

    # Vessels Search Report
    "tools/vintrace_playwright_vessels_report.py",

    # Analysis Export Report & melt 
    "tools/vintrace_playwright_analysis_report.py",
    "tools/vintrace_analysis_process.py",
    

    #Trigger dat Refresh
    "tools/power_auto_trigger.py"
]

# Number of times to loop through the list
num_loops = 1
for i in range(num_loops):
    print(f"Loop {i+1}/{num_loops}")
    for script in python_scripts:
        print(f"Running {script}...")
        result = subprocess.run(["python", script])
        if result.returncode != 0:
            print(f"{script} exited with error code {result.returncode}")
        else:
            print(f"{script} finished successfully.")
    time.sleep(60)  # seconds between loops

print("All loops complete.")