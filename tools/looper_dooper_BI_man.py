# python tools/looper_dooper_BI_man.py





import subprocess
import time

# List of Python scripts to run
python_scripts = [


    # All Barrels Report
    "tools/vintrace_playwright_Barrel_Report.py",

    # Vessels Search Report
    "tools/vintrace_playwright_vessels_report.py",

    # Analysis Export Report & melt 
    "tools/vintrace_playwright_analysis_report.py",
    "tools/vintrace_analysis_process.py",
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