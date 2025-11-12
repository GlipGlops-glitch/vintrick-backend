import json
import os
import pandas as pd
from sqlalchemy import create_engine, text

from utils.helpers import convert_epoch_columns, trim_and_log  

# --- CONFIG ---
DATABASE_URL = os.getenv("DB_URL")
DATA_DIR = "/app/Main/data/GET--transactions_by_day/tables/"

COL_MAX_LENGTHS = {
    "transactions": {
        "ts_operationTypeName": 100,
        "ts_subOperationTypeName": 100,
        "ts_formattedDate": 20,
        "ts_workorder": 50,
        "ts_treatment": 100,
        "ts_assignedBy": 100,
        "ts_completedBy": 100,
        "ts_winery": 100,
    },
    "transactions_from_vessel": {
        "ts_name": 50,
        "ts_volOutUnit": 10,
    },
    "transactions_to_vessel": {
        "ts_name": 50,
        "ts_volInUnit": 10,
    },
    "transactions_loss_details": {
        "ts_volumeUnit": 10,
        "ts_reason": 100,
    },
    "transactions_analysis_ops": {
        "ts_vesselName": 50,
        "ts_batchName": 50,
        "ts_templateName": 100,
    },
    "transactions_metrics": {
        "ts_metric_name": 50,
        "ts_metric_txtValue": 20,
        "ts_metric_unit": 20,
    },
}

FILE_TABLE_MAP = {
    "transactions.json": "transactions",
    "transactions_from_vessel.json": "transactions_from_vessel",
    "transactions_from_vessel_before_details.json": "transactions_from_vessel_before_details",
    "transactions_from_vessel_after_details.json": "transactions_from_vessel_after_details",
    "transactions_to_vessel.json": "transactions_to_vessel",
    "transactions_to_vessel_before_details.json": "transactions_to_vessel_before_details",
    "transactions_to_vessel_after_details.json": "transactions_to_vessel_after_details",
    "transactions_loss_details.json": "transactions_loss_details",
    "transactions_analysis_ops.json": "transactions_analysis_ops",
    "transactions_metrics.json": "transactions_metrics"
}

UPSERT_PK_MAP = {
    "transactions": "ts_id",
    "transactions_from_vessel": "ts_from_vessel_id",
    "transactions_from_vessel_before_details": "ts_before_details_id",
    "transactions_from_vessel_after_details": "ts_after_details_id",
    "transactions_to_vessel": "ts_to_vessel_id",
    "transactions_to_vessel_before_details": "ts_before_details_id",
    "transactions_to_vessel_after_details": "ts_after_details_id",
    "transactions_loss_details": "ts_loss_details_id",
    "transactions_analysis_ops": "ts_analysis_ops_id",
    "transactions_metrics": "ts_metrics_id"
}

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Please add to .env or environment.")

engine = create_engine(DATABASE_URL, fast_executemany=True)

def serialize_dict_columns(df):
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, dict)).any():
            df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
    return df

def deduplicate_dataframe(df, pk_col):
    """Remove duplicate PKs, keeping the last occurrence."""
    if pk_col in df.columns:
        before = len(df)
        df = df.drop_duplicates(subset=[pk_col], keep='last')
        after = len(df)
        num_dropped = before - after
        if num_dropped > 0:
            print(f"Deduplication: Dropped {num_dropped} duplicate rows for PK {pk_col}")
    return df

def load_and_insert_new_records(filename, table_name, engine):
    pk_col = UPSERT_PK_MAP[table_name]
    path = os.path.join(DATA_DIR, filename)
    print(f"Checking for new records in {path} for table '{table_name}'...")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df = convert_epoch_columns(df)

    float_columns_map = {
        "transactions": [
            "ts_jobNumber",
            "ts_date",
            "ts_lastModified"
        ],
        "transactions_from_vessel": [
            "ts_volOut"
        ],
        "transactions_to_vessel": [
            "ts_volIn"
        ],
        "transactions_loss_details": [
            "ts_volume"
        ],
        "transactions_from_vessel_before_details": [
            "ts_volume"
        ],
        "transactions_from_vessel_after_details": [
            "ts_volume"
        ],
        "transactions_to_vessel_before_details": [
            "ts_volume"
        ],
        "transactions_to_vessel_after_details": [
            "ts_volume"
        ],
        "transactions_metrics": [
            "ts_metric_value"
        ]
    }
    float_columns = float_columns_map.get(table_name, [])
    for col in float_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = serialize_dict_columns(df)
    df = deduplicate_dataframe(df, pk_col)

    if table_name in COL_MAX_LENGTHS:
        df = trim_and_log(df, COL_MAX_LENGTHS[table_name])

    # Get existing PKs from database
    with engine.connect() as conn:
        query = f"SELECT {pk_col} FROM {table_name}"
        existing_pks = pd.read_sql(query, conn)[pk_col].astype(str).tolist()

    # Only keep rows whose PK is not in the table
    new_df = df[~df[pk_col].astype(str).isin(existing_pks)]

    if new_df.empty:
        print(f"No new records to upload to {table_name}.")
    else:
        new_df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Uploaded {len(new_df)} new records to {table_name}.")

ordered_table_files = [
    ("transactions.json", "transactions"),
    ("transactions_from_vessel.json", "transactions_from_vessel"),
    ("transactions_to_vessel.json", "transactions_to_vessel"),
    ("transactions_loss_details.json", "transactions_loss_details"),
    ("transactions_analysis_ops.json", "transactions_analysis_ops"),
    ("transactions_from_vessel_before_details.json", "transactions_from_vessel_before_details"),
    ("transactions_from_vessel_after_details.json", "transactions_from_vessel_after_details"),
    ("transactions_to_vessel_before_details.json", "transactions_to_vessel_before_details"),
    ("transactions_to_vessel_after_details.json", "transactions_to_vessel_after_details"),
    ("transactions_metrics.json", "transactions_metrics"),
]

def main():
    for filename, table_name in ordered_table_files:
        load_and_insert_new_records(filename, table_name, engine)

if __name__ == "__main__":
    main()