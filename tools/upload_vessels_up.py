import json
import os
import pandas as pd
from sqlalchemy import create_engine

from utils.helpers import convert_epoch_columns, trim_and_log  

# --- CONFIG ---
DATABASE_URL = os.getenv("DB_URL")
DATA_DIR = "/app/Main/data/GET--vessels/tables/"

# --- ADD MAX LENGTHS FOR TRIMMING ---
COL_MAX_LENGTHS = {
    "vessels_wine_batch": {
        "vs_batch_name": 50,
        "vs_batch_description": 100,
        "vs_batch_program": 25,
        "vs_batch_grading": 25,
        "vs_batch_productCategory": 50,
        "vs_batch_designatedProduct": 50,
        "vs_batch_designatedVariety_code": 25,
        "vs_batch_designatedVariety_name": 100,
        "vs_batch_designatedRegion_code": 25,
        "vs_batch_designatedRegion_name": 100,
        "vs_batch_designatedSubRegion": 100,
        "vs_batch_vintage": 10,
        # add more as needed!
    },
}

# Mapping from filename to table name (filename without extension)
FILE_TABLE_MAP = {
    "vessels.json": "vessels",
    "vessels_wine_batch.json": "vessels_wine_batch",
    "vessels_composition.json": "vessels_composition",
    "vessels_cost.json": "vessels_cost",
    "vessels_ttb_details.json": "vessels_ttb_details"
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
    path = os.path.join(DATA_DIR, filename)
    print(f"Uploading {path} to table '{table_name}'...")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    # Convert all epoch time columns to datetime using helper
    df = convert_epoch_columns(df)

    float_columns_map = {
        "vessels": [
            'vs_productState_expectedLossesPercentage',
            'vs_volume_value',
            'vs_capacity_value',
            'vs_ullage_value',
            'vs_ttbDetails_alcoholPercentage'
        ],
        "vessels_wine_batch": [
            "vs_batch_id",
            "vs_batch_designatedVariety_id",
            "vs_batch_designatedRegion_id"
            # Add more float columns if you add them to your schema
        ],
        "vessels_composition": [
            'vs_weighting',
            'vs_percentage',
            'vs_componentVolume_value',
            'vs_CompGal'
        ],
        "vessels_cost": [
            'vs_total',
            'vs_fruit',
            'vs_overhead',
            'vs_storage',
            'vs_additive',
            'vs_bulk',
            'vs_packaging',
            'vs_operation',
            'vs_freight',
            'vs_other'
        ],
        "vessels_ttb_details": [
            'vs_alcoholPercentage'
        ]
    }

    float_columns = float_columns_map.get(table_name, [])
    for col in float_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = serialize_dict_columns(df)

    # --- TRIM AND LOG OVERLONG VALUES ---
    if table_name in COL_MAX_LENGTHS:
        df = trim_and_log(df, COL_MAX_LENGTHS[table_name])

    # Set chunksize based on table
    chunk = 5000 if table_name == "vessels_composition" else 1000
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