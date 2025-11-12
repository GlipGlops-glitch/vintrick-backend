# python tools/vintrace_system_audit.py

import os
import pdfplumber
import json

# Directory containing PDFs
pdf_dir = "Main/data/vintrace_reports/system_audit"

fields = [
    "Type",
    "Started",
    "Stopped",
    "(mm:ss)",
    "Status",
    "User",
    "Summary"
]

pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
if not pdf_files:
    raise FileNotFoundError(f"No PDF files found in {pdf_dir}")

pdf_path = os.path.join(pdf_dir, pdf_files[0])
output_json = pdf_path.replace('.pdf', '.json')

data_list = []
header_row = None

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for table in tables:
            if not table or len(table) < 2:
                continue
            if page_num == 0:
                # First page: get header from PDF, and store
                header_row = table[0]
                # Map indices for desired fields
                field_indices = []
                for f in fields:
                    try:
                        idx = header_row.index(f)
                    except ValueError:
                        idx = None
                    field_indices.append(idx)
                data_rows = table[1:]
            else:
                # Later pages: assume header missing, use stored indices
                data_rows = table
            # Process each data row
            for row in data_rows:
                entry = {}
                for field, idx in zip(fields, field_indices):
                    entry[field] = row[idx] if idx is not None and idx < len(row) else ""
                data_list.append(entry)

with open(output_json, "w") as f:
    json.dump(data_list, f, indent=2)

print(f"Extracted {len(data_list)} rows. Saved to {output_json}")