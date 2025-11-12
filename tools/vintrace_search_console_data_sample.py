#  python tools/vintrace_search_console_data_sample.py
import os
import csv
import json
import re
from collections import defaultdict

CSV_DIR = "Main/data/vintrace_reports/disp_console_sample/"
OUT_FILE = "Main/data/vintrace_reports/disp_console_sample/merged_all_sample.json"
MAX_RECORDS = 100000000  # Output only this many merged records

def parse_csv_filename(filename):
    m = re.match(
        r"report_(\d+)_BOL_(.+?)_Date_(.+?)_Qty_(.+?)_Code_(.+)\.csv", filename
    )
    if not m:
        return None
    return {
        "idx": m.group(1),
        "bol": m.group(2),
        "date": m.group(3),
        "qty": m.group(4),
        "code": m.group(5),
        "file": filename
    }

def extract_origin_fields(origin):
    if not origin or "[" not in origin:
        return {}
    m = re.search(r"\[(.*?)\]", origin)
    if not m:
        return {}
    inner = m.group(1)
    match = re.match(
        r"(?P<vintage>\d{4})\s+(?P<ava>\w+)\s+--\s+(?P<variety>\w+)\s+\[.*\b(?P<block>[A-Z0-9]+)\]$", inner
    )
    if not match:
        match = re.match(
            r"(?P<vintage>\d{4})\s+(?P<ava>\w+)\s+--\s+(?P<variety>\w+).*?(?P<block>[A-Z0-9]+)$", inner
        )
    if match:
        return match.groupdict()
    return {}

COLUMN_MAP = {
    "origin":           ("Bulk Wine Origin", "Grapes [Grower Block] Origin"),
    "weigh_tag":        ("Weigh tag #",      "Weigh tag #"),
    "block_vintage":    (None,               "Block/Vintage"),
    "delivery_date":    ("Delivery Date",    "Delivery Date"),
    "percent":          ("Percent",          "Percent"),
    "relative_volume":  ("Relative Volume",  "Relative Volume"),
}

files = [f for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
groups = defaultdict(dict)
for fn in files:
    meta = parse_csv_filename(fn)
    if meta:
        key = (meta["bol"], meta["date"], meta["qty"], meta["code"])
        groups[key][meta["idx"]] = fn

merged_records = []
count = 0

for key, pair in groups.items():
    if count >= MAX_RECORDS:
        break
    if "1" not in pair or "2" not in pair:
        print(f"Skipping incomplete pair for {key}")
        continue
    file1 = os.path.join(CSV_DIR, pair["1"])
    file2 = os.path.join(CSV_DIR, pair["2"])
    with open(file1, newline='', encoding='utf-8') as f1:
        reader1 = list(csv.DictReader(f1))
    with open(file2, newline='', encoding='utf-8') as f2:
        reader2 = list(csv.DictReader(f2))

    merged_rows = []
    maxlen = max(len(reader1), len(reader2))
    for i in range(maxlen):
        bulk_row = reader1[i] if i < len(reader1) else {}
        fruit_row = reader2[i] if i < len(reader2) else {}
        merged_row = {
            "date": key[1],
            "bol": key[0],
            "quantity": key[2]
        }
        for merged_key, (bulk_col, fruit_col) in COLUMN_MAP.items():
            value = None
            if bulk_col and bulk_col in bulk_row and bulk_row[bulk_col] != '':
                value = bulk_row[bulk_col]
            elif fruit_col and fruit_col in fruit_row:
                value = fruit_row[fruit_col]
            merged_row[merged_key] = value
        origin_info = extract_origin_fields(merged_row.get("origin", ""))
        merged_row.update(origin_info)
        merged_rows.append(merged_row)

    merged_records.append({
        "bol": key[0],
        "date": key[1],
        "quantity": key[2],
        "code": key[3],
        "bulk_csv": pair["1"],
        "fruit_csv": pair["2"],
        "merged_rows": merged_rows,
    })
    count += 1

with open(OUT_FILE, "w", encoding="utf-8") as out:
    json.dump(merged_records, out, indent=2)

print(f"Done! Wrote {len(merged_records)} merged records to {OUT_FILE} (sample)")