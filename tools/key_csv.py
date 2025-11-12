#    python tools/key_csv.py

import json
import csv

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def main(json_path, csv_path, x):
    # Load first x records from JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # If the JSON file is a list of records
        records = data[:x]

    # Flatten each record
    flat_records = [flatten_dict(rec) for rec in records]

    # Collect all keys
    all_keys = set()
    for rec in flat_records:
        all_keys.update(rec.keys())
    all_keys = sorted(all_keys)

    # Write to CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_keys)
        writer.writeheader()
        for rec in flat_records:
            writer.writerow(rec)

if __name__ == "__main__":
    # Example usage
    main(
        # json_path='Main/data/GET--transactions_by_day/transactions_2024-10-08.json',
        json_path='Main/data/GET--shipments/all_shipments.json',
           # your input JSON file
        csv_path='tools/key_field_ship.csv',    # your output CSV file
        x=10                     # number of records to export
    )