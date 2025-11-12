# python tools/vintrace_transactions_report_test.py


import csv
import json
import os

REPORT_FILENAME = "vintrace_transactions.csv"
CSV_INPUT_PATH = os.path.join("Main", "data", "vintrace_reports", REPORT_FILENAME)

TARGET_SAVE_DIR = os.path.join("Main", "data", "vintrace_reports")
os.makedirs(TARGET_SAVE_DIR, exist_ok=True)
JSON_FILENAME = "vintrace_transaction_report.json"
JSON_FILE_PATH = os.path.join(TARGET_SAVE_DIR, JSON_FILENAME)

def csv_to_json_table(csv_path, json_path):
    """Reads a CSV file and outputs a JSON array of objects, omitting columns with no data."""
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = []
        columns_with_data = set()
        all_rows = list(reader)
        for row in all_rows:
            for k, v in row.items():
                if v and v.strip():
                    columns_with_data.add(k)
        for row in all_rows:
            filtered_row = {k: v for k, v in row.items() if k in columns_with_data}
            rows.append(filtered_row)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    csv_to_json_table(CSV_INPUT_PATH, JSON_FILE_PATH)