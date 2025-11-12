#python tools/vintrace_workdetail_parse2.py

import os
import csv
import json

REPORT_FILENAME = "workdetail.csv"
CSV_INPUT_PATH = os.path.join("Main", "data", "vintrace_reports", REPORT_FILENAME)
TARGET_SAVE_DIR = os.path.join("Main", "data", "vintrace_reports")
os.makedirs(TARGET_SAVE_DIR, exist_ok=True)
JSON_FILENAME = "workdetail_keyvalue.json"
JSON_FILE_PATH = os.path.join(TARGET_SAVE_DIR, JSON_FILENAME)

def normalize_keyvalue(in_path):
    """
    Reads workdetail.csv, detects work orders, and produces
    a normalized JSON where each operation's data is a dict mapping columns to values.
    """
    work_orders = []
    with open(in_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        current_work_order = None
        current_section = None
        last_subheader = None
        last_section_type = None
        section_blocks = []

        for row in reader:
            # Detect blank row
            if not any(cell.strip() for cell in row):
                continue

            # Detect new work order (starts with CC/CR in col 0)
            if row[0].startswith("CC") or row[0].startswith("CR"):
                # Save previous work order
                if current_work_order:
                    current_work_order['operations'] = section_blocks
                    work_orders.append(current_work_order)
                # Start new work order
                current_work_order = {
                    "header": {
                        "Work Order": row[0],
                        "Job #": row[1],
                        "Date": row[2],
                        "Job Type": row[3],
                        "Operation Id": row[4],
                        "Treatment": row[5],
                        "Assigned By": row[6],
                        "Completed By": row[7]
                    }
                }
                section_blocks = []
                current_section = None
                last_subheader = None
                last_section_type = None
                continue

            # Section header (e.g. 'Treatment', 'Transfer', etc.)
            if row[0] == "" and row[1] in (
                "Treatment", "Transfer", "Adjustment", "Extraction", "Addition",
                "StartFerment", "BulkDispatchDetail", "MoveToBatch", "Delivery", "Intake"
            ):
                current_section = row[1]
                last_section_type = current_section
                last_subheader = None
                continue

            # Subheader or data (starts with "", "")
            if row[0] == "" and row[1] == "":
                # If this row has column names (starts with 3 empty then text, e.g. "To Vessel")
                if any(cell.strip() for cell in row[3:]):
                    # If last_subheader is None, treat this as column header
                    if last_subheader is None:
                        last_subheader = row
                        continue
                    else:
                        # If last_subheader is not None, treat this as data row paired with last_subheader
                        cols = last_subheader[3:]
                        vals = row[3:]
                        section_blocks.append({
                            "section": last_section_type,
                            "data": dict(zip(cols, vals))
                        })
                        last_subheader = None
                        continue
                else:
                    # Row is just empty, skip
                    continue

            # For other rows (e.g. Treatment section), treat first as columns, next as data
            if current_section and last_section_type == "Treatment":
                # If last_subheader is None, treat as columns header
                if last_subheader is None:
                    last_subheader = row
                else:
                    cols = last_subheader[2:]
                    vals = row[2:]
                    section_blocks.append({
                        "section": last_section_type,
                        "data": dict(zip(cols, vals))
                    })
                    last_subheader = None
                continue

            # For other single-line sections (Addition, Extraction, etc.)
            if current_section and last_section_type not in ("Transfer", "Treatment"):
                # These are usually simple one-line columns/data
                if last_subheader is None:
                    last_subheader = row
                else:
                    cols = last_subheader[2:]
                    vals = row[2:]
                    section_blocks.append({
                        "section": last_section_type,
                        "data": dict(zip(cols, vals))
                    })
                    last_subheader = None
                continue

        # Save final work order
        if current_work_order:
            current_work_order['operations'] = section_blocks
            work_orders.append(current_work_order)
    return work_orders

if __name__ == "__main__":
    work_orders = normalize_keyvalue(CSV_INPUT_PATH)
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(work_orders, f, indent=2, ensure_ascii=False)
    print(f"Key/value normalized work order data written to {JSON_FILE_PATH}")