import json
import os
import pandas as pd
from sqlalchemy import create_engine

from tools.utils.helpers import convert_epoch_columns  # <-- Import your helper

# --- CONFIG ---
DATABASE_URL = os.getenv("DB_URL")
DATA_DIR = "/app/Main/data/GET--shipments/tables/"

# Mapping from filename to table name (filename without extension)
FILE_TABLE_MAP = {
    "shipments.json": "shipments",
    "shipments_wine_details.json": "shipments_wine_details",
    "shipments_wine_batch.json": "shipments_wine_batch",
    "shipments_composition.json": "shipments_composition"
}

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Please add to .env or environment.")

# Enable fast_executemany for pyodbc
engine = create_engine(DATABASE_URL, fast_executemany=True)

def serialize_dict_columns(df):
    # Convert any columns with dicts to JSON strings
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, dict)).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
    return df

def upload_json_to_sql(filename, table_name, engine):
    import math
    path = os.path.join(DATA_DIR, filename)
    print(f"Uploading {path} to table '{table_name}'...")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    # Convert all epoch time columns to datetime using helper
    df = convert_epoch_columns(df)

    float_columns_map = {
        "shipments_wine_details": [
            'weight',
            'volume_value',
            'loss_volume_value',
            'loss_reason_id'
        ],
        "shipments_wine_batch": [
            # add float columns if needed for this table
        ],
        "shipments_composition": [
            # add float columns if needed for this table
        ],
        "shipments": [
            # add float columns if needed for this table
        ]
    }

    float_columns = float_columns_map.get(table_name, [])
    for col in float_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = serialize_dict_columns(df)

    # Set chunksize based on table
    chunk = 5000 if table_name == "shipments_composition" else 1000
    total_rows = len(df)
    print(f"Total rows to insert into '{table_name}': {total_rows}")

    # Progress tracker
    percent_checkpoints = [int(total_rows * x / 100) for x in range(10, 101, 10)]
    next_checkpoint_idx = 0

    rows_inserted = 0
    try:
        # Use to_sql with chunksize but manually iterate for progress
        for i in range(0, total_rows, chunk):
            end = min(i + chunk, total_rows)
            df_chunk = df.iloc[i:end]
            df_chunk.to_sql(table_name, engine, if_exists='append', index=False)
            rows_inserted += len(df_chunk)

            # Print progress at each checkpoint
            while (next_checkpoint_idx < len(percent_checkpoints) and 
                   rows_inserted >= percent_checkpoints[next_checkpoint_idx]):
                percent = (next_checkpoint_idx + 1) * 10
                print(f"{percent}% complete ({rows_inserted}/{total_rows} rows inserted)")
                next_checkpoint_idx += 1

        print(f"Uploaded {total_rows} rows to table '{table_name}'")

    except Exception as e:
        print(f"Failed to upload {table_name}: {e}")
        print("Columns:", df.columns.tolist())
        if len(df) > 0:
            print("Sample row:", df.iloc[0].to_dict())
        raise

def main():
    for filename, table_name in FILE_TABLE_MAP.items():
        upload_json_to_sql(filename, table_name, engine)
    print("All tables uploaded.")

if __name__ == "__main__":
    main()