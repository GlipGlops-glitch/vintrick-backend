# python tools/looper_dooper_BI_man.py

import subprocess
import time
import shlex

# List of Python scripts to run
python_scripts = [


    # Dispatch Console Reports
    "tools/vintrace_playwright_dispatch_search_console.py --mode recent --days 7",
    "tools/vintrace_playwright_dispatch_search_console.py --mode missing",
    "tools/vintrace_playwright_dispatch_search_console.py --mode fetch --csv missing_dispatches.csv",
    "tools/vintrace_search_console_data.py",
]

# Number of times to loop through the list
num_loops = 1
for i in range(num_loops):
    print(f"Loop {i+1}/{num_loops}")
    for script in python_scripts:
        print(f"Running {script}...")
        # Split the script command properly to handle arguments
        cmd_parts = shlex.split(script)
        result = subprocess.run(["python"] + cmd_parts)
        if result.returncode != 0:
            print(f"{script} exited with error code {result.returncode}")
        else:
            print(f"{script} finished successfully.")
    time.sleep(60)  # seconds between loops

print("All loops complete.")