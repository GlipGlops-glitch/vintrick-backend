# python tools/stip_header.py

import os
import json

INPUT_DIR = "Main/data/GET--transactions_by_day/"  # Change if needed

def is_top_level_obj_with_transactions(data):
    return isinstance(data, dict) and "transactionSummaries" in data

def is_array_of_top_level_objs(data):
    return (
        isinstance(data, list) and
        len(data) > 0 and
        all(isinstance(item, dict) and "transactionSummaries" in item for item in data)
    )

for fname in os.listdir(INPUT_DIR):
    path = os.path.join(INPUT_DIR, fname)
    if not fname.endswith('.json') or not os.path.isfile(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"ERROR parsing {fname}: {e}")
            continue

    new_data = None

    # Case 1: top-level dict with transactionSummaries
    if is_top_level_obj_with_transactions(data):
        new_data = data["transactionSummaries"]

    # Case 2: array of dicts with transactionSummaries
    elif is_array_of_top_level_objs(data):
        # Concatenate all transactionSummaries arrays together
        all_ts = []
        for item in data:
            all_ts.extend(item["transactionSummaries"])
        new_data = all_ts

    elif isinstance(data, list):
        print(f"No change: {fname} is already an array of transactions.")
    else:
        print(f"{fname} is not a recognized format (skipped).")

    if new_data is not None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(new_data, f, indent=2)
        print(f"Stripped top-level keys from {fname}")