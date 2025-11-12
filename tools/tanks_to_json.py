#python tools/tanks_to_json.py


import csv
import json

# Input and output file names


csv_file = 'Main/data/excel_reports/Tanks_All.csv'
json_file = 'Main/data/id_tables/Tanks_All.json'

# Read CSV and convert to list of dicts
with open(csv_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Write to JSON
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(rows, f, indent=2)

print(f"Converted {csv_file} to {json_file}")