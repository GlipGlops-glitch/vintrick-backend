import json
import os
import pandas as pd
from sqlalchemy import create_engine

from utils.helpers import convert_epoch_columns, trim_and_log

# --- CONFIG ---
DATABASE_URL = os.getenv("DB_URL")
DATA_DIR = "/app/Main/data/GET--intakes/tables/"

# --- ADD MAX LENGTHS FOR TRIMMING ---
COL_MAX_LENGTHS = {
    "intakes": {
        "in_vessel": 50,
        "in_batch": 50,
        "in_fractionType": 25,
        "in_fermentState": 25,
        "in_malolacticState": 25,
        "in_productType": 25,
        "in_beverageType": 25,
        "in_reference": 50,
        "in_batchOwner_name": 100,
        "in_batchOwner_extId": 100,
    },
    "intakes_composition": {
        "in_block_name": 100,
        "in_block_extId": 100,
        "in_region_name": 100,
        "in_subRegion_name": 100,
        "in_variety_name": 100,
    },
    "intakes_cost": {},
    "intakes_ttb_details": {
        "in_bond_name": 100,
        "in_taxState": 25,
        "in_taxClass_name": 50,
        "in_taxClass_federalName": 50,
        "in_taxClass_stateName": 50,
    },
    "intakes_delivery": {
        "in_purchaseOrder_name": 100,
        "in_receivedFrom_name": 100,
        "in_carrier_name": 100,
        "in_shippingRefNo": 100,
        "in_truckNo": 25,
        "in_driverName": 100,
        "in_sealNo": 50,
        "in_compartmentNo": 25,
        "in_cipNo": 25,
        "in_container": 50,
        "in_customsEntryNumber": 50,
        "in_purchaseReference": 100,
        "in_deliveryState": 25,
    },
    "intakes_metrics": {
        "in_metric_name": 100,
        "in_metric_nonNumericValue": 100,
        "in_metric_interfaceMappedName": 100,
    },
}

# Mapping from filename to table name (filename without extension)
FILE_TABLE_MAP = {
    "intakes.json": "intakes",
    "intakes_composition.json": "intakes_composition",
    "intakes_cost.json": "intakes_cost",
    "intakes_ttb_details.json": "intakes_ttb_details",
    "intakes_delivery.json": "intakes_delivery",
    "intakes_metrics.json": "intakes_metrics"
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
        "intakes": [
            "in_occurredTime",
            "in_volume_value",
        ],
        "intakes_composition": [
            "in_percentage",
            "in_vintage",
            "in_CompGal",
            "in_region_id",
            "in_subRegion_id",
            "in_variety_id",
            "in_block_id"
        ],
        "intakes_cost": [
            "in_amount",
        ],
        "intakes_ttb_details": [
            "in_taxClass_id",
            "in_alcoholPercentage",
            "in_bond_id"
        ],
        "intakes_delivery": [
            "in_purchaseOrder_id",
            "in_receivedFrom_id",
            "in_carrier_id"
        ],
        "intakes_metrics": [
            "in_metric_value"
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