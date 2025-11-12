import json
import os
import pandas as pd
from sqlalchemy import create_engine

from utils.helpers import convert_epoch_columns, trim_and_log

# --- CONFIG ---
DATABASE_URL = os.getenv("DB_URL")
DATA_DIR = "/app/Main/data/GET--fruit_intakes/tables/"

# --- ADD MAX LENGTHS FOR TRIMMING ---
COL_MAX_LENGTHS = {
    "fruit_intakes": {
        "fi_bookingNumber": 50,
        "fi_block_name": 100,
        "fi_block_externalCode": 50,
        "fi_vineyard_name": 100,
        "fi_winery_name": 100,
        "fi_grower_name": 100,
        "fi_region_name": 100,
        "fi_region_shortCode": 25,
        "fi_variety_name": 100,
        "fi_variety_shortCode": 25,
        "fi_owner_name": 100,
        "fi_owner_shortCode": 25,
        "fi_driverName": 100,
        "fi_truckRegistration": 50,
        "fi_consignmentNote": 50,
        "fi_docketNo": 50,
        "fi_amount_unit": 10,
        "fi_grossAmount_unit": 10,
        "fi_tareAmount_unit": 10,
        "fi_harvestMethod": 25,
        "fi_intendedUse": 100,
        "fi_growerContract_name": 100,
        "fi_fruitCostRateType": 20,
        "fi_externalWeighTag": 50,
        "fi_additionalDetails": 500,
    },
    "fruit_intakes_metrics": {
        "fi_metricName": 50,
        "fi_metricShortCode": 25,
        "fi_metric_unit": 10,
    }
}

# Mapping from filename to table name (filename without extension)
FILE_TABLE_MAP = {
    "fruit_intakes.json": "fruit_intakes",
    "fruit_intakes_metrics.json": "fruit_intakes_metrics"
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
        "fruit_intakes": [
            "fi_effectiveDate",
            "fi_modified",
            "fi_deliveryStart",
            "fi_deliveryEnd",
            "fi_amount_value",
            "fi_grossAmount_value",
            "fi_tareAmount_value",
            "fi_fruitCost",
            "fi_area",
            "fi_vintage",
            "fi_block_id",
            "fi_vineyard_id",
            "fi_winery_id",
            "fi_grower_id",
            "fi_region_id",
            "fi_variety_id",
            "fi_owner_id",
            "fi_growerContract_id",
        ],
        "fruit_intakes_metrics": [
            "fi_metric_value",
            "fi_metric_recorded",
            "fi_metricId"
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

    chunk = 1000
    total_rows = len(df)
    print(f"Total rows to insert into '{table_name}': {total_rows}")

    percent_checkpoints = [int(total_rows * x / 100) for x in range(10, 101, 10)]
    next_checkpoint_idx = 0

    rows_inserted = 0
    try:
        for i in range(0, total_rows, chunk):
            end = min(i + chunk, total_rows)
            df_chunk = df.iloc[i:end]
            df_chunk.to_sql(table_name, engine, if_exists='append', index=False)
            rows_inserted += len(df_chunk)

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