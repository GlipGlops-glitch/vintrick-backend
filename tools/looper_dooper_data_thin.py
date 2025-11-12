# python tools/looper_dooper_data_thin.py

import subprocess
import time
import multiprocessing

# --- Script group definitions ---

# Group 1: Power BI script (independent)
power_bi_scripts = {
    
    "tools/power_auto_trigger.py": 600  # run every 5 minutes
}

# Group 2: Dispatch Console + Work Detailz Reports (independent)
dispatch_workdetailz_scripts = {


    # # Work Detailz Reports
    # "tools/vintrace_playwright_work_detailz.py": 900,
    
}

# Group 3: All other scripts
other_scripts = {

    # Fruit Intakes API
    "tools/fetch_fruit_intakes.py": 900,
    "tools/upload_fruit_intakes_main.py": 900,

    # Grape Delivery Report
    "tools/vintrace_Grape_Report_with_bookingSummary_playwright.py": 900,
    "tools/vintrace_grape_report_detail.py": 900,
    
        # Dispatch Console Reports
    "tools/vintrace_playwright_dispatch_search_console_recent_7.py": 900,
    "tools/vintrace_playwright_dispatch_search_console_missing.py": 600,
    "tools/vintrace_playwright_dispatch_search_console_fix_partials.py": 600,
    "tools/vintrace_search_console_data.py": 600,


        # Work Detailz Reports
    "tools/vintrace_playwright_work_detailz.py": 900,


    "tools/vintrace_work_detail_extract_parcel_weightag_glob_convert_v2.py": 600,
    "tools/vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_Disp.py": 600,
    "tools/vintrace_work_detail_extract_parcel_weightag_glob_convert_v2_onHand.py": 600,


    
}

def run_scripts_group(scripts, group_name, num_loops=100000, check_interval=10):
    last_run = {script: 0 for script in scripts}
    for i in range(num_loops):
        print(f"[{group_name}] Loop {i+1}/{num_loops}")
        now = time.time()
        for script, sleep_time in scripts.items():
            if now - last_run[script] >= sleep_time:
                print(f"[{group_name}] Running {script}...")
                # Handle full command or just script name
                cmd = script.split() if script.startswith("python ") else ["python", script]
                result = subprocess.run(cmd)
                last_run[script] = now
                if result.returncode != 0:
                    print(f"[{group_name}] {script} exited with error code {result.returncode}")
                else:
                    print(f"[{group_name}] {script} finished successfully.")
            else:
                remaining = int(sleep_time - (now - last_run[script]))
                print(f"[{group_name}] Skipping {script}; next run in {remaining} seconds.")
        time.sleep(check_interval)
    print(f"[{group_name}] All loops complete.")

if __name__ == "__main__":
    processes = []

    # Start Power BI group process
    processes.append(multiprocessing.Process(
        target=run_scripts_group,
        args=(power_bi_scripts, "PowerBI")
    ))

    # Start Dispatch+WorkDetailz group process
    processes.append(multiprocessing.Process(
        target=run_scripts_group,
        args=(dispatch_workdetailz_scripts, "DispatchWorkDetailz")
    ))

    # Start Other scripts group process
    processes.append(multiprocessing.Process(
        target=run_scripts_group,
        args=(other_scripts, "OtherScripts")
    ))

    # Start all processes
    for p in processes:
        p.start()
    # Optionally, wait for all processes to finish
    for p in processes:
        p.join()