# python tools/upload_transactions_main_up.py

import json
import os
import pandas as pd
from sqlalchemy import create_engine

from utils.helpers import convert_epoch_columns, trim_and_log  

# --- CONFIG ---
DATABASE_URL = os.getenv("DB_URL")
DATA_DIR = "/app/Main/data/GET--transactions_by_day/tables/"
ORPHAN_EXPORT_DIR = "/app/Main/data/GET--transactions_by_day/orphan_exports/"
os.makedirs(ORPHAN_EXPORT_DIR, exist_ok=True)

COL_MAX_LENGTHS = {
    "ts_transactions": {
        "ts_operationTypeName": 100,
        "ts_subOperationTypeName": 100,
        "ts_formattedDate": 20,
        "ts_workorder": 50,
        "ts_treatment": 100,
        "ts_assignedBy": 100,
        "ts_completedBy": 100,
        "ts_winery": 100,
    },
    "ts_transactions_from_vessel": {
        "ts_name": 50,
        "ts_volOutUnit": 10,
    },
    "ts_transactions_to_vessel": {
        "ts_name": 50,
        "ts_volInUnit": 10,
    },
    "ts_transactions_loss_details": {
        "ts_volumeUnit": 10,
        "ts_reason": 100,
    },
    "ts_transactions_analysis_metrics": {
        "ts_vesselName": 50,
        "ts_batchName": 50,
        "ts_templateName": 100,
        "ts_metric_name": 50,
        "ts_metric_txtValue": 20,
        "ts_metric_unit": 20,
    },
    "ts_transactions_from_vessel_before_details": {},
    "ts_transactions_from_vessel_after_details": {},
    "ts_transactions_to_vessel_before_details": {},
    "ts_transactions_to_vessel_after_details": {},
    "ts_transactions_additional_details": {
        "ts_summary": 100,
        "ts_bookingNo": 50,
        "ts_owner": 100,
        "ts_netAmountUnit": 20,
        "ts_vintage": 20,
        "ts_subAva": 50,
        "ts_block": 50,
        "ts_varietal": 50,
        "ts_grower": 100,
        "ts_dockets": 50,
        "ts_harvestMethod": 50,
        "ts_dispatchNo": 50,
        "ts_crusher": 50,
        "ts_fruitProcess": 50,
        "ts_fractionType": 50,
        "ts_press": 50,
    },
    "ts_transactions_extraction_parcels": {
        "ts_docket": 20,
        "ts_bookingNo": 50,
        "ts_growerName": 100,
        "ts_vineyardName": 100,
        "ts_blockName": 50,
        "ts_weightUnit": 10,
    },
    "ts_transactions_addition_ops": {
        "ts_vesselName": 50,
        "ts_batchName": 50,
        "ts_templateName": 100,
        "ts_changeToState": 50,
        "ts_unit": 10,
        "ts_lotNumbers": 100,
        "ts_additive_name": 50,
        "ts_additive_description": 100,
    }
}

FILE_TABLE_MAP = {
    "transactions.json": "ts_transactions",
    "transactions_from_vessel.json": "ts_transactions_from_vessel",
    "transactions_from_vessel_before_details.json": "ts_transactions_from_vessel_before_details",
    "transactions_from_vessel_after_details.json": "ts_transactions_from_vessel_after_details",
    "transactions_to_vessel.json": "ts_transactions_to_vessel",
    "transactions_to_vessel_before_details.json": "ts_transactions_to_vessel_before_details",
    "transactions_to_vessel_after_details.json": "ts_transactions_to_vessel_after_details",
    "transactions_loss_details.json": "ts_transactions_loss_details",
    "transactions_analysis_metrics.json": "ts_transactions_analysis_metrics",
    "transactions_additional_details.json": "ts_transactions_additional_details",
    "transactions_extraction_parcels.json": "ts_transactions_extraction_parcels",
    "transactions_addition_ops.json": "ts_transactions_addition_ops",
}

UPSERT_PK_MAP = {
    "ts_transactions": "ts_subOperationTypeId",
    "ts_transactions_from_vessel": "ts_subOperationTypeId",
    "ts_transactions_from_vessel_before_details": "ts_subOperationTypeId",
    "ts_transactions_from_vessel_after_details": "ts_subOperationTypeId",
    "ts_transactions_to_vessel": "ts_subOperationTypeId",
    "ts_transactions_to_vessel_before_details": "ts_subOperationTypeId",
    "ts_transactions_to_vessel_after_details": "ts_subOperationTypeId",
    "ts_transactions_loss_details": "ts_subOperationTypeId",
    "ts_transactions_analysis_metrics": ["ts_subOperationTypeId", "ts_metric_id"],  # composite PK
    "ts_transactions_additional_details": "ts_subOperationTypeId",
    "ts_transactions_extraction_parcels": "ts_docket",
    "ts_transactions_addition_ops": "ts_subOperationTypeId",
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
    before = len(df)
    if isinstance(pk_col, list):
        df = df.drop_duplicates(subset=pk_col, keep='last')
    else:
        if pk_col in df.columns:
            df = df.drop_duplicates(subset=[pk_col], keep='last')
    after = len(df)
    num_dropped = before - after
    if num_dropped > 0:
        print(f"Deduplication: Dropped {num_dropped} duplicate rows for PK {pk_col}")
    return df

def remove_null_pks(df, pk_col):
    if isinstance(pk_col, list):
        for pk in pk_col:
            df = df[df[pk].notnull()]
    else:
        df = df[df[pk_col].notnull()]
    return df

def remove_reversed_records(df):
    if "ts_reversed" in df.columns:
        mask = ~((df["ts_reversed"] == True) | (df["ts_reversed"].astype(str).str.lower() == "true"))
        df = df[mask]
    return df

def find_and_export_orphans(df, table_name, engine):
    """
    For child tables with FK to ts_transactions, export orphan records to Excel.
    Returns df without orphans.
    """
    child_fk_map = {
        "ts_transactions_from_vessel": "ts_subOperationTypeId",
        "ts_transactions_from_vessel_before_details": "ts_subOperationTypeId",
        "ts_transactions_from_vessel_after_details": "ts_subOperationTypeId",
        "ts_transactions_to_vessel": "ts_subOperationTypeId",
        "ts_transactions_to_vessel_before_details": "ts_subOperationTypeId",
        "ts_transactions_to_vessel_after_details": "ts_subOperationTypeId",
        "ts_transactions_loss_details": "ts_subOperationTypeId",
        "ts_transactions_analysis_metrics": "ts_subOperationTypeId",
        "ts_transactions_additional_details": "ts_subOperationTypeId",
    }
    fk_col = child_fk_map.get(table_name)
    if fk_col:
        with engine.connect() as conn:
            valid_pks = pd.read_sql("SELECT ts_subOperationTypeId FROM ts_transactions", conn)["ts_subOperationTypeId"].astype(str)
        df[fk_col] = df[fk_col].astype(str)
        mask = ~df[fk_col].isin(valid_pks)
        orphan_df = df[mask]
        if not orphan_df.empty:
            export_path = os.path.join(ORPHAN_EXPORT_DIR, f"{table_name}_orphans.xlsx")
            orphan_df.to_excel(export_path, index=False)
            print(f"Exported {len(orphan_df)} orphan rows from {table_name} to {export_path}")
        # Only returning non-orphans in case you want to inspect later
        df = df[~mask]
    return df

def test_orphan_export_only(filename, table_name, engine):
    pk_col = UPSERT_PK_MAP[table_name]
    path = os.path.join(DATA_DIR, filename)
    print(f"Testing orphan export in {path} for table '{table_name}'...")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df = convert_epoch_columns(df)

    float_columns_map = {
        "ts_transactions": [],
        "ts_transactions_from_vessel": ["ts_volOut"],
        "ts_transactions_to_vessel": ["ts_volIn"],
        "ts_transactions_loss_details": ["ts_volume"],
        "ts_transactions_from_vessel_before_details": ["ts_volume"],
        "ts_transactions_from_vessel_after_details": ["ts_volume"],
        "ts_transactions_to_vessel_before_details": ["ts_volume"],
        "ts_transactions_to_vessel_after_details": ["ts_volume"],
        "ts_transactions_analysis_metrics": ["ts_metric_value"],
        "ts_transactions_extraction_parcels": ["ts_weight"],
        "ts_transactions_addition_ops": ["ts_amount"],
    }
    float_columns = float_columns_map.get(table_name, [])
    for col in float_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = serialize_dict_columns(df)
    df = deduplicate_dataframe(df, pk_col)
    df = remove_reversed_records(df)
    df = remove_null_pks(df, pk_col)
    if table_name in COL_MAX_LENGTHS:
        df = trim_and_log(df, COL_MAX_LENGTHS[table_name])

    # Find and export orphans (does not upload anything)
    _ = find_and_export_orphans(df, table_name, engine)

ordered_table_files = [
    ("transactions_from_vessel.json", "ts_transactions_from_vessel"),
    ("transactions_from_vessel_before_details.json", "ts_transactions_from_vessel_before_details"),
    ("transactions_from_vessel_after_details.json", "ts_transactions_from_vessel_after_details"),
    ("transactions_to_vessel.json", "ts_transactions_to_vessel"),
    ("transactions_to_vessel_before_details.json", "ts_transactions_to_vessel_before_details"),
    ("transactions_to_vessel_after_details.json", "ts_transactions_to_vessel_after_details"),
    ("transactions_loss_details.json", "ts_transactions_loss_details"),
    ("transactions_analysis_metrics.json", "ts_transactions_analysis_metrics"),
    ("transactions_additional_details.json", "ts_transactions_additional_details"),
    # You can add more here if you want to test them
]

def main():
    for filename, table_name in ordered_table_files:
        test_orphan_export_only(filename, table_name, engine)

if __name__ == "__main__":
    main()