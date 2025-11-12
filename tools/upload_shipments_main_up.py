#python tools/upload_shipments_main_up.py

import json
import os
import pandas as pd
from sqlalchemy import create_engine, text

from utils.helpers import trim_and_log

DATABASE_URL = os.getenv("DB_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Please add to .env or environment.")

# --- Refactored DATA_DIR to use Vintrick/vintrick-data/Main/data ---
DATA_DIR_1 = "/app/Main/data/GET--shipments/tables/"
DATA_DIR_2 = "/app/Main/data/GET--transactions_by_day/tables/"
engine = create_engine(DATABASE_URL, fast_executemany=True)

SHIP_TABLE_VARCHAR_LENGTHS = {
    "shipments": {
        "shipment_id": 20,
        "workOrderNumber": 20,
        "jobNumber": 20,
        "shipmentNumber": 20,
        "type": 50,
        "occurredTime": 30,
        "modifiedTime": 30,
        "reference": 50,
        "freightCode": 20,
        "reversed": 10,
        "source_id": 20,
        "source_name": 50,
        "source_businessUnit": 50,
        "destination_winery_name": 50,
        "destination_party_id": 20,
        "destination_party_name": 50,
        "carrier": 50,
        "dispatchType_id": 20,
        "dispatchType_name": 50,
    },
    "shipments_wine_details": {
        "shipment_id": 20,
        "wine_details_id": 50,
        "vessel": 50,
        "batch": 50,
        "weight": 20,
        "volume_unit": 20,
        "volume_value": 20,
        "loss_volume_unit": 20,
        "loss_volume_value": 20,
        "loss_reason_id": 20,
        "loss_reason_name": 50,
        "bottlingDetails": 100,
        "wineryBuilding_id": 20,
        "wineryBuilding_name": 50,
    },
    "shipments_wine_batch": {
        "shipment_id": 20,
        "wine_details_id": 50,
        "id": 20,
        "name": 50,
        "description": 100,
        "vintage": 20,
        "program": 50,
        "designatedRegion_id": 20,
        "designatedRegion_name": 50,
        "designatedRegion_code": 20,
        "designatedVariety_id": 20,
        "designatedVariety_name": 50,
        "designatedVariety_code": 20,
        "productCategory_id": 20,
        "productCategory_name": 50,
        "productCategory_code": 20,
        "designatedProduct_id": 20,
        "designatedProduct_name": 50,
        "designatedProduct_code": 20,
        "grading_scaleId": 20,
        "grading_scaleName": 50,
        "grading_valueId": 20,
        "grading_valueName": 50,
        "cost_total": 20,
        "cost_fruit": 20,
        "cost_overhead": 20,
        "cost_storage": 20,
        "cost_additive": 20,
        "cost_bulk": 20,
        "cost_packaging": 20,
        "cost_operation": 20,
        "cost_freight": 20,
        "cost_other": 20,
        "cost_average": 20
    },
    "shipments_composition": {
        "shipment_id": 20,
        "wine_details_id": 50,
        "percentage": 20,
        "vintage": 20,
        "subRegion": 50,
        "block_id": 20,
        "block_name": 50,
        "block_extId": 20,
        "region_id": 20,
        "region_name": 50,
        "variety_id": 20,
        "variety_name": 50,
        "CompGal": 20
    },
    "unique_dispatchNos_table": {
        "ts_dispatchNo": 20,
        "ts_subOperationId": 20,
        "ts_formattedDate": 20,
        "ts_workorder": 20,
        "ts_jobNumber": 20,
        "ts_treatment": 100,
        "ts_completedBy": 100,
        "ts_winery": 100
    },
    "shipments_composition_sample_20": {
        "shipment_id": 20,
        "wine_details_id": 50,
        "percentage": 20,
        "vintage": 20,
        "subRegion": 50,
        "block_id": 20,
        "block_name": 50,
        "block_extId": 20,
        "region_id": 20,
        "region_name": 50,
        "variety_id": 20,
        "variety_name": 50,
        "CompGal": 20
    }
}

UPSERT_PK_MAP = {
    "shipments": "shipment_id",
    "shipments_wine_details": ["shipment_id", "wine_details_id"],
    "shipments_wine_batch": ["shipment_id", "wine_details_id"],
    "shipments_composition": ["shipment_id", "wine_details_id", "block_id", "variety_id"],
    "unique_dispatchNos_table": "ts_dispatchNo",
    "shipments_composition_sample_20": ["shipment_id", "wine_details_id", "block_id", "variety_id"]
}

def get_varchar_lengths(engine, table_name):
    query = f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = '{table_name}'
        AND DATA_TYPE IN ('varchar', 'nvarchar', 'char', 'nchar')
    """
    with engine.connect() as conn:
        rows = conn.execute(text(query)).fetchall()
        return {row[0]: row[2] for row in rows}

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

def trim_all_varchar_cols(df, sql_col_max_lengths, static_col_max_lengths):
    all_col_max_lengths = dict(sql_col_max_lengths)
    all_col_max_lengths.update(static_col_max_lengths)
    print(f"Trimming columns to max lengths: {all_col_max_lengths}")

    missing_in_static = set(sql_col_max_lengths) - set(static_col_max_lengths)
    if missing_in_static:
        print(f"WARNING: These string columns are in SQL but not your static dict: {missing_in_static}")

    for col, maxlen in all_col_max_lengths.items():
        if col in df.columns and pd.api.types.is_string_dtype(df[col]):
            trimmed = df[col].astype(str).str.slice(0, maxlen)
            over_limit = df[col].astype(str).str.len() > maxlen
            if over_limit.any():
                for idx in df[over_limit].index:
                    val = df.at[idx, col]
                    print(f"TRIMMED: Column '{col}' value '{val}' to length {maxlen}")
            df[col] = trimmed

    for col, maxlen in all_col_max_lengths.items():
        if col in df.columns and pd.api.types.is_string_dtype(df[col]):
            still_over = df[col].astype(str).str.len() > maxlen
            if still_over.any():
                print(f"ERROR: Still over limit in column '{col}'. Number of offending rows: {still_over.sum()}")
                print(df.loc[still_over, col].head(5))
    return df

def parse_formatted_date(df, col="ts_formattedDate"):
    """Parse MM/DD/YYYY to pandas date, then to string YYYY-MM-DD for SQL DATE"""
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], format="%m/%d/%Y", errors="coerce")
        df[col] = df[col].dt.strftime("%Y-%m-%d")
    return df

def bulk_insert_records(df, table_name, engine, chunk_size=10000):
    sql_col_max_lengths = get_varchar_lengths(engine, table_name)
    for col, maxlen in sql_col_max_lengths.items():
        if col in df.columns and isinstance(maxlen, int) and pd.api.types.is_string_dtype(df[col]):
            still_over = df[col].astype(str).str.len() > maxlen
            if still_over.any():
                print(f"FINAL ERROR: Upload will fail: column '{col}' has {still_over.sum()} values longer than {maxlen} chars")
                print(df.loc[still_over, col].head())
                raise ValueError(f"Column {col} has values over its limit after trimming. Fix your mapping or add to the trim function.")
    df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=chunk_size)

ordered_table_files = [
    # ("shipments.json", "shipments"),
    # ("shipments_wine_details.json", "shipments_wine_details"),
    # ("shipments_wine_batch.json", "shipments_wine_batch"),
    # ("shipments_composition.json", "shipments_composition"),
    ("unique_dispatchNos_table.json", "ts_ad_dispatches"),  # Integrate for ts_ad_dispatches
    # ("shipments_composition_sample_20.json", "shipments_composition_sample_20"),
]

def main():
    for filename, table_name in ordered_table_files:
        pk_col = UPSERT_PK_MAP.get(table_name, "ts_dispatchNo")
        # Use SHIPMENTS_DIR for shipments, TRANSACTIONS_DIR for transactions_by_day
        # For ts_ad_dispatches, use SHIPMENTS_DIR
        if table_name == "ts_ad_dispatches":
            path = os.path.join(DATA_DIR_1, filename)
        else:
            path = os.path.join(DATA_DIR_2, filename)
        print(f"\nProcessing: {path} -> {table_name}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded records from JSON: {len(data)}")
        print(f"First 3 records: {data[:3]}")
        df = pd.DataFrame(data)
        # Only keep columns matching your schema for ts_ad_dispatches
        if table_name == "ts_ad_dispatches":
            keep_cols = [
                "ts_dispatchNo",
                "ts_subOperationId",
                "ts_formattedDate",
                "ts_workorder",
                "ts_jobNumber",
                "ts_treatment",
                "ts_completedBy",
                "ts_winery"
            ]
            df = df[keep_cols]
            # Parse and format date
            df = parse_formatted_date(df, col="ts_formattedDate")
            # Ensure jobNumber and subOperationId are numeric
            df["ts_jobNumber"] = pd.to_numeric(df["ts_jobNumber"], errors="coerce").astype("Int64")
            df["ts_subOperationId"] = pd.to_numeric(df["ts_subOperationId"], errors="coerce").astype("Int64")
        sql_col_max_lengths = get_varchar_lengths(engine, table_name)
        static_col_max_lengths = SHIP_TABLE_VARCHAR_LENGTHS.get(table_name, {})
        print(f"SQL schema max lengths for {table_name}: {sql_col_max_lengths}")
        print(f"Static mapping max lengths for {table_name}: {static_col_max_lengths}")
        df = trim_all_varchar_cols(df, sql_col_max_lengths, static_col_max_lengths)
        df = serialize_dict_columns(df)
        df = remove_null_pks(df, pk_col)
        df = deduplicate_dataframe(df, pk_col)
        print(df.dtypes)
        print(df.head())
        bulk_insert_records(df, table_name, engine, chunk_size=10000)
        print(f"Uploaded {len(df)} records to {table_name}.")

if __name__ == "__main__":
    main()