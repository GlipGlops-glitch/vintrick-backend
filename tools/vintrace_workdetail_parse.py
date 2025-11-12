#python tools/vintrace_workdetail_parse.py


import os
import csv
import json

REPORT_FILENAME = "workdetail.csv"
CSV_INPUT_PATH = os.path.join("Main", "data", "vintrace_reports", REPORT_FILENAME)

TARGET_SAVE_DIR = os.path.join("Main", "data", "vintrace_reports")
os.makedirs(TARGET_SAVE_DIR, exist_ok=True)
JSON_FILENAME = "workdetail.json"
JSON_FILE_PATH = os.path.join(TARGET_SAVE_DIR, JSON_FILENAME)

def parse_complex_csv(filename):
    work_orders = []
    current_work_order = None
    current_job = None
    current_section = None
    current_headers = None

    def flush_job():
        nonlocal current_work_order, current_job
        if current_job:
            current_work_order['jobs'].append(current_job)
            current_job = None

    def flush_work_order():
        nonlocal current_work_order
        if current_work_order:
            work_orders.append(current_work_order)
            current_work_order = None

    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if not any(cell.strip() for cell in row):
                continue
            if row[0].startswith('CC') or row[0].startswith('CR'):
                flush_job()
                flush_work_order()
                current_work_order = {
                    'work_order': row[0],
                    'job_number': row[1],
                    'date': row[2],
                    'job_type': row[3],
                    'operation_id': row[4],
                    'treatment': row[5],
                    'assigned_by': row[6],
                    'completed_by': row[7],
                    'jobs': []
                }
                current_section = None
                current_headers = None
                continue
            if row[1] in (
                'Treatment', 'Transfer', 'Adjustment', 'Extraction', 'Addition',
                'StartFerment', 'BulkDispatchDetail', 'MoveToBatch', 'Delivery', 'Intake'
            ):
                current_section = row[1]
                current_headers = [cell for cell in row if cell]
                continue
            if current_section and current_headers:
                section_data = {}
                for idx, header in enumerate(current_headers):
                    section_data[header] = row[idx+2] if idx+2 < len(row) else ''
                if not current_job:
                    current_job = {
                        'section': current_section,
                        'events': []
                    }
                current_job['events'].append(section_data)
                continue
            if row[1] in ('Delivery', 'Intake'):
                if not current_job:
                    current_job = {
                        'section': row[1],
                        'events': []
                    }
                current_job['events'].append({'info': row[2]})
                continue

    flush_job()
    flush_work_order()
    return work_orders

if __name__ == "__main__":
    data = parse_complex_csv(CSV_INPUT_PATH)
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Parsed data has been saved to {JSON_FILE_PATH}.")