# vintrick-backend/tools/upload_shipments_flat.py
# Recursively flattens nested JSON (list of shipments), builds a DataFrame, and uploads to SQL Server.
# Usage: python tools/upload_shipments_flat.py

import pandas as pd
import json
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
JSON_PATH = os.getenv("SHIPMENTS_JSON", "Main/data/GET--shipments/10_shipments.json")
TABLE_NAME = os.getenv("SHIPMENTS_TABLE", "shipments_flat")
DATABASE_URL = os.getenv("DATABASE_URL")  # Should match SQLAlchemy format (mssql+pyodbc://...)

# --- FULL RECURSIVE FLATTEN ---
def flatten_json(obj, parent_key='', sep='.'):
    """Recursively flattens dicts and lists into dot-separated keys."""
    items = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_json(v, new_key, sep=sep).items())
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(flatten_json(v, new_key, sep=sep).items())
    else:
        items.append((parent_key, obj))
    return dict(items)

# --- LOAD AND FLATTEN ---
with open(JSON_PATH, "r", encoding="utf-8") as f:
    shipments = json.load(f)

flat_rows = []
for s in shipments:
    flat_rows.append(flatten_json(s))

df = pd.DataFrame(flat_rows)

# --- CLEAN COLUMN NAMES FOR SQL ---
# Replace problematic chars (if needed)
df.columns = [c.replace('[', '_').replace(']', '_').replace(' ', '_').replace('-', '_').replace('.', '__') for c in df.columns]

# --- ERROR HANDLING FOR UPLOAD ---
def safe_to_sql(df, table_name, engine):
    """Attempts to upload DataFrame to SQL, handles errors, prints diagnostics."""
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Uploaded {len(df)} rows to table '{table_name}'")
    except Exception as e:
        print("Upload failed:", e)
        # Print diagnostics for debugging
        print("DataFrame columns:", df.columns.tolist())
        print("Sample row:", df.iloc[0].to_dict())
        # Raise for visibility
        raise

# --- CONNECT TO SQL SERVER AND UPLOAD ---
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Please add to .env or environment.")

engine = create_engine(DATABASE_URL)
safe_to_sql(df, TABLE_NAME, engine)

print("All done! Flat upload complete.")

"""
NOTES:
- This creates one wide/flat table with all possible nested keys as columns.
- Nested arrays (e.g. wineDetails.0.composition.3.variety_name) become columns like wineDetails__0__composition__3__variety__name.
- If a field is missing in a record, column value is NaN/null.
- For analytics/ETL, this is optimal. For normalized/relational, use separate tables.
- You can change sep to '_' or another char if you prefer.
"""