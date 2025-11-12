#   python tools/vintrace_work_detail_extract_parcel_weightag.py

import csv
import json
import re
import chardet

def detect_encoding(file_path, sample_size=4096):
    """Detect text encoding for robust CSV reading."""
    with open(file_path, 'rb') as f:
        raw = f.read(sample_size)
    result = chardet.detect(raw)
    encoding = result['encoding']
    print(f"[INFO] Detected encoding: {encoding}")
    return encoding if encoding else "utf-8"

def extract_grouped_fields(csv_filename, json_filename):
    encoding = detect_encoding(csv_filename)
    events = []  # List of (row_idx, type, value)

    with open(csv_filename, newline='', encoding=encoding, errors="replace") as csvfile:
        reader = csv.reader(csvfile)
        for row_idx, row in enumerate(reader):
            if not any(cell.strip() for cell in row):  # skip blank rows
                continue
            for cell in row:
                # Intake
                intake_match = re.search(r'Delivery intake #([A-Za-z0-9]+)', cell)
                if intake_match:
                    events.append((row_idx, "intake", intake_match.group(1)))
                # Delivery
                delivery_match = re.search(r'Delivery #([A-Za-z0-9]+)', cell)
                if delivery_match:
                    events.append((row_idx, "delivery", delivery_match.group(1)))

    # Now pair each delivery with the closest intake (before or after)
    records = []
    seen_pairs = set()
    for i, (row_idx, typ, val) in enumerate(events):
        if typ == "delivery":
            # Find nearest intake (before or after)
            nearest_intake = None
            nearest_dist = None
            for j, (other_row_idx, other_typ, other_val) in enumerate(events):
                if other_typ == "intake":
                    dist = abs(other_row_idx - row_idx)
                    if nearest_dist is None or dist < nearest_dist:
                        nearest_dist = dist
                        nearest_intake = other_val
            if nearest_intake:
                tup = (val, nearest_intake)
                if tup not in seen_pairs:
                    records.append({"Delivery": val, "Intake": nearest_intake})
                    seen_pairs.add(tup)

    with open(json_filename, 'w', encoding="utf-8") as jsonfile:
        json.dump(records, jsonfile, indent=4)

if __name__ == "__main__":
    file_path = 'Main/data/vintrace_reports/work_detailz.csv'
    output_path = 'Main/data/vintrace_reports/work_detailz.json'
    extract_grouped_fields(file_path, output_path)