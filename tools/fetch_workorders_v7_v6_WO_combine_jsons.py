# python tools/fetch_workorders_v7_v6_WO_combine_jsons.py

import os
import json
from glob import glob

# Directory containing individual work order JSON files
input_dir = "Main/data/GET--work_orders_paged/v6_details"
# Output file path for the combined JSON
output_file = "Main/data/GET--work_orders_paged/all_workorders_combined.json"

# Get a sorted list of JSON files in the directory
json_files = sorted(glob(os.path.join(input_dir, "*.json")))

combined = []
skipped = 0

for file in json_files:
    try:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Skip files that are error dumps instead of work order data
            if isinstance(data, dict) and "error" in data:
                skipped += 1
                continue
            combined.append(data)
    except Exception as e:
        print(f"Failed to load {file}: {e}")
        skipped += 1

print(f"Loaded {len(combined)} work orders, skipped {skipped} files with errors or invalid JSON.")

# Write the combined JSON array to the output file
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(combined, f, indent=2, ensure_ascii=False)

print(f"Combined JSON written to {output_file}")