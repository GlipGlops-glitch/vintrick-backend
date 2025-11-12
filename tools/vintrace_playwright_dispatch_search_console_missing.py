#  python tools/vintrace_playwright_dispatch_search_console_missing.py
import os
import csv
import re

CSV_SAVE_DIR = "Main/data/vintrace_reports/disp_console/"
ALL_DISPATCHES_CSV = "Main/data/vintrace_reports/all_dispatches.csv"

def sanitize_filename(s):
    return re.sub(r'[\\/*?:"<>|]', '_', str(s))

def normalize_date(date_str):
    """Converts CSV date (M/D/YYYY or MM/DD/YYYY) to MM-DD-YYYY (with leading zeros)."""
    parts = date_str.strip().replace("-", "/").split("/")
    if len(parts) == 3:
        mm = parts[0].zfill(2)
        dd = parts[1].zfill(2)
        yyyy = parts[2]
        return f"{mm}-{dd}-{yyyy}"
    return date_str

def load_all_dispatches(csv_path):
    """Loads all dispatches as a list of dicts with keys: date, bol, quantity, code."""
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = []
        for row in reader:
            records.append({
                "date": normalize_date(row["date"].strip()),
                "bol": row["bol"].strip(),
                "quantity": row["quantity"].strip(),
                "code": row["code"].strip()
            })
        return records

def already_downloaded_files():
    """Returns a set of records (date, bol, quantity, code) for which both CSVs exist."""
    existing = set()
    files = os.listdir(CSV_SAVE_DIR)
    pattern = r"report_1_BOL_(.+?)_Date_(.+?)_Qty_(.+?)_Code_(.+)\.csv"
    for fn in files:
        m = re.match(pattern, fn)
        if m:
            bol = m.group(1)
            date = m.group(2)  # already in MM-DD-YYYY
            quantity = m.group(3)
            code = m.group(4)
            bulk_fn = f"report_1_BOL_{sanitize_filename(bol)}_Date_{sanitize_filename(date)}_Qty_{sanitize_filename(quantity)}_Code_{sanitize_filename(code)}.csv"
            fruit_fn = f"report_2_BOL_{sanitize_filename(bol)}_Date_{sanitize_filename(date)}_Qty_{sanitize_filename(quantity)}_Code_{sanitize_filename(code)}.csv"
            if bulk_fn in files and fruit_fn in files:
                existing.add((sanitize_filename(date), sanitize_filename(bol), sanitize_filename(quantity), sanitize_filename(code)))
    return existing

def main():
    all_dispatches = load_all_dispatches(ALL_DISPATCHES_CSV)
    fetched = already_downloaded_files()

    print("First 5 dispatches from CSV (normalized & sanitized):")
    for rec in all_dispatches[:5]:
        print((sanitize_filename(rec["date"]), sanitize_filename(rec["bol"]), sanitize_filename(rec["quantity"]), sanitize_filename(rec["code"])))

    print("\nFirst 5 keys already fetched from files:")
    for key in list(fetched)[:5]:
        print(key)

    missing = []
    for rec in all_dispatches:
        key = (sanitize_filename(rec["date"]), sanitize_filename(rec["bol"]), sanitize_filename(rec["quantity"]), sanitize_filename(rec["code"]))
        if key not in fetched:
            missing.append(rec)

    print(f"\nTotal dispatches in CSV: {len(all_dispatches)}")
    print(f"Already fetched: {len(fetched)}")
    print(f"Missing (need to fetch): {len(missing)}")
    if missing:
        out_csv = "Main/data/vintrace_reports/disp_console/missing_dispatches.csv"
        with open(out_csv, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["date", "bol", "quantity", "code"])
            writer.writeheader()
            writer.writerows(missing)
        print(f"Wrote missing dispatches to {out_csv}")
    else:
        print("No missing dispatches!")

if __name__ == "__main__":
    main()