import json
import os
import pandas as pd
from sqlalchemy import create_engine, text

from utils.helpers import convert_epoch_columns, trim_and_log  

DATABASE_URL = os.getenv("DB_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Please add to .env or environment.")

DATA_DIR = "/app/Main/data/GET--transactions_by_day/tables/"
engine = create_engine(DATABASE_URL, fast_executemany=True)

# --- SQL authoritative VARCHAR/NVARCHAR/CHAR/NCHAR columns and max lengths ---
TS_TABLE_VARCHAR_LENGTHS = {
    # ... (as in your original) ...
    "ts_transactions": {
        "ts_assignedBy": 100,
        "ts_completedBy": 100,
        "ts_formattedDate": 20,
        "ts_jobNumber": 50,
        "ts_operationId": 50,
        "ts_operationTypeId": 50,
        "ts_operationTypeName": 100,
        "ts_subOperationId": 50,
        "ts_subOperationTypeName": 100,
        "ts_treatment": 100,
        "ts_winery": 100,
        "ts_workorder": 50,
    },
    "ts_transactions_addition_ops": {
        "ts_additive_description": 100,
        "ts_additive_id": 50,
        "ts_additive_name": 50,
        "ts_batchId": 50,
        "ts_batchName": 50,
        "ts_changeToState": 50,
        "ts_lotNumbers": 100,
        "ts_templateId": 50,
        "ts_templateName": 100,
        "ts_unit": 10,
        "ts_vesselId": 50,
        "ts_vesselName": 50,
        "ts_volume": 50,
    },
    "ts_transactions_additional_details": {
        "ts_block": 50,
        "ts_bookingNo": 50,
        "ts_crusher": 50,
        "ts_dispatchNo": 50,
        "ts_dockets": 50,
        "ts_fractionType": 50,
        "ts_fruitProcess": 50,
        "ts_grower": 100,
        "ts_harvestMethod": 50,
        "ts_netAmountUnit": 20,
        "ts_owner": 100,
        "ts_press": 50,
        "ts_subAva": 50,
        "ts_summary": 100,
        "ts_varietal": 50,
        "ts_vintage": 20,
    },
    "ts_transactions_analysis_metrics": {
        "ts_batchId": 50,
        "ts_batchName": 50,
        "ts_metric_id": 50,
        "ts_metric_name": 50,
        "ts_metric_txtValue": 20,
        "ts_metric_unit": 20,
        "ts_templateId": 50,
        "ts_templateName": 100,
        "ts_vesselId": 50,
        "ts_vesselName": 50,
    },


    "ts_transactions_from_vessel": {
        "ts_name": 50,
        "ts_vessel_id": 50,
        "ts_volOutUnit": 10,
    },
    "ts_transactions_from_vessel_after_details": {
        "ts_alcoholicFermentState": 50,
        "ts_batch": 50,
        "ts_batchDetails_description": 100,
        "ts_batchDetails_name": 50,
        "ts_batchDetails_region_id": 20,
        "ts_batchDetails_region_name": 20,
        "ts_batchDetails_variety_id": 20,
        "ts_batchDetails_variety_name": 20,
        "ts_batchDetails_vintage_id": 20,
        "ts_batchDetails_vintage_name": 20,
        "ts_batchId": 50,
        "ts_batchOwner": 50,
        "ts_contentsId": 50,
        "ts_dip": 20,
        "ts_federalTaxClass": 20,
        "ts_grading": 50,
        "ts_malolacticFermentState": 50,
        "ts_physicalStateText": 100,
        "ts_productCategory": 50,
        "ts_program": 50,
        "ts_rawTaxClass": 20,
        "ts_revisionName": 50,
        "ts_serviceOrder": 50,
        "ts_state": 20,
        "ts_stateTaxClass": 20,
        "ts_volumeUnit": 20,
    },
    "ts_transactions_from_vessel_before_details": {
        "ts_alcoholicFermentState": 50,
        "ts_batch": 50,
        "ts_batchDetails_description": 100,
        "ts_batchDetails_name": 50,
        "ts_batchDetails_region_id": 20,
        "ts_batchDetails_region_name": 20,
        "ts_batchDetails_variety_id": 20,
        "ts_batchDetails_variety_name": 20,
        "ts_batchDetails_vintage_id": 20,
        "ts_batchDetails_vintage_name": 20,
        "ts_batchId": 50,
        "ts_batchOwner": 50,
        "ts_contentsId": 50,
        "ts_dip": 20,
        "ts_federalTaxClass": 20,
        "ts_grading": 50,
        "ts_malolacticFermentState": 50,
        "ts_physicalStateText": 100,
        "ts_productCategory": 50,
        "ts_program": 50,
        "ts_rawTaxClass": 20,
        "ts_revisionName": 50,
        "ts_serviceOrder": 50,
        "ts_state": 20,
        "ts_stateTaxClass": 20,
        "ts_volumeUnit": 20,
    },
    "ts_transactions_loss_details": {
        "ts_reason": 100,
        "ts_volumeUnit": 10,
    },
    "ts_transactions_to_vessel": {
        "ts_name": 50,
        "ts_vessel_id": 50,
        "ts_volInUnit": 10,
    },
    "ts_transactions_to_vessel_after_details": {
        "ts_alcoholicFermentState": 50,
        "ts_batch": 50,
        "ts_batchDetails_description": 100,
        "ts_batchDetails_name": 50,
        "ts_batchDetails_region_id": 20,
        "ts_batchDetails_region_name": 20,
        "ts_batchDetails_variety_id": 20,
        "ts_batchDetails_variety_name": 20,
        "ts_batchDetails_vintage_id": 20,
        "ts_batchDetails_vintage_name": 20,
        "ts_batchId": 50,
        "ts_batchOwner": 50,
        "ts_contentsId": 50,
        "ts_dip": 20,
        "ts_federalTaxClass": 20,
        "ts_grading": 50,
        "ts_malolacticFermentState": 50,
        "ts_physicalStateText": 100,
        "ts_productCategory": 50,
        "ts_program": 50,
        "ts_rawTaxClass": 20,
        "ts_revisionName": 50,
        "ts_serviceOrder": 50,
        "ts_state": 20,
        "ts_stateTaxClass": 20,
        "ts_volumeUnit": 20,
    },
    "ts_transactions_to_vessel_before_details": {
        "ts_alcoholicFermentState": 50,
        "ts_batch": 50,
        "ts_batchDetails_description": 100,
        "ts_batchDetails_name": 50,
        "ts_batchDetails_region_id": 20,
        "ts_batchDetails_region_name": 20,
        "ts_batchDetails_variety_id": 20,
        "ts_batchDetails_variety_name": 20,
        "ts_batchDetails_vintage_id": 20,
        "ts_batchDetails_vintage_name": 20,
        "ts_batchId": 50,
        "ts_batchOwner": 50,
        "ts_contentsId": 50,
        "ts_dip": 20,
        "ts_federalTaxClass": 20,
        "ts_grading": 50,
        "ts_malolacticFermentState": 50,
        "ts_physicalStateText": 100,
        "ts_productCategory": 50,
        "ts_program": 50,
        "ts_rawTaxClass": 20,
        "ts_revisionName": 50,
        "ts_serviceOrder": 50,
        "ts_state": 20,
        "ts_stateTaxClass": 20,
        "ts_volumeUnit": 20,
    },
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
    "ts_transactions_analysis_metrics": ["ts_subOperationTypeId", "ts_metric_id"],
    "ts_transactions_additional_details": "ts_subOperationTypeId",
    "ts_transactions_extraction_parcels": "ts_docket",
    "ts_transactions_addition_ops": "ts_subOperationTypeId",
}

def get_varchar_lengths(engine, table_name):
    """
    Returns a dict of column_name: max_length for all VARCHAR/NVARCHAR/CHAR/NCHAR columns in the given table in SQL Server.
    """
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

def remove_reversed_records(df):
    if "ts_reversed" in df.columns:
        mask = ~((df["ts_reversed"] == True) | (df["ts_reversed"].astype(str).str.lower() == "true"))
        df = df[mask]
    return df

def enforce_pk_types(df, pk_col):
    if isinstance(pk_col, list):
        for pk in pk_col:
            if pk in df.columns:
                df[pk] = pd.to_numeric(df[pk], errors='coerce').astype('Int64')
    else:
        if pk_col in df.columns:
            df[pk_col] = pd.to_numeric(df[pk_col], errors='coerce').astype('Int64')
    return df

def trim_all_varchar_cols(df, sql_col_max_lengths, static_col_max_lengths):
    """
    Trims all string columns to their SQL column max length. If not in the static dict, uses SQL introspection.
    Warns about any columns not present in static dict.
    """
    # Merge static and SQL introspected lengths: static dict overrides SQL.
    all_col_max_lengths = dict(sql_col_max_lengths)
    all_col_max_lengths.update(static_col_max_lengths)

    print(f"Trimming columns to max lengths: {all_col_max_lengths}")

    # Warn about columns in SQL but not in your static mapping.
    missing_in_static = set(sql_col_max_lengths) - set(static_col_max_lengths)
    if missing_in_static:
        print(f"WARNING: These string columns are in SQL but not your static dict: {missing_in_static}")

    # Trim all columns to their max lengths
    for col, maxlen in all_col_max_lengths.items():
        if col in df.columns and pd.api.types.is_string_dtype(df[col]):
            trimmed = df[col].astype(str).str.slice(0, maxlen)
            over_limit = df[col].astype(str).str.len() > maxlen
            if over_limit.any():
                for idx in df[over_limit].index:
                    val = df.at[idx, col]
                    print(f"TRIMMED: Column '{col}' value '{val}' to length {maxlen}")
            df[col] = trimmed

    # After trimming, check for any still over limit
    for col, maxlen in all_col_max_lengths.items():
        if col in df.columns and pd.api.types.is_string_dtype(df[col]):
            still_over = df[col].astype(str).str.len() > maxlen
            if still_over.any():
                print(f"ERROR: Still over limit in column '{col}'. Number of offending rows: {still_over.sum()}")
                print(df.loc[still_over, col].head(5))
    return df

# Example returned mapping:
# {'ts_docket': ('VARCHAR', 20), 'ts_growerId': ('INT', None), ...}

def bulk_insert_records(df, table_name, engine, chunk_size=10000):
    # Get max lengths for actual VARCHAR columns in SQL table
    sql_col_max_lengths = get_varchar_lengths(engine, table_name)

    # Only check columns that are both in max_lengths AND are string dtype in pandas
    for col, maxlen in sql_col_max_lengths.items():
        # Check pandas dtype AND skip if column is INT/FLOAT in SQL
        # (You can also keep a list of which columns are VARCHAR in SQL)
        if col in df.columns:
            # Check if SQL expects VARCHAR
            if isinstance(maxlen, int) and pd.api.types.is_string_dtype(df[col]):
                still_over = df[col].astype(str).str.len() > maxlen
                if still_over.any():
                    print(f"FINAL ERROR: Upload will fail: column '{col}' has {still_over.sum()} values longer than {maxlen} chars")
                    print(df.loc[still_over, col].head())
                    raise ValueError(f"Column {col} has values over its limit after trimming. Fix your mapping or add to the trim function.")
    df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=chunk_size)

ordered_table_files = [
    # ("transactions.json", "ts_transactions"),
    # ("transactions_from_vessel.json", "ts_transactions_from_vessel"),
    # ("transactions_to_vessel.json", "ts_transactions_to_vessel"),
    # ("transactions_loss_details.json", "ts_transactions_loss_details"),
    # ("transactions_analysis_metrics.json", "ts_transactions_analysis_metrics"),
    # ("transactions_from_vessel_before_details.json", "ts_transactions_from_vessel_before_details"),
    # ("transactions_from_vessel_after_details.json", "ts_transactions_from_vessel_after_details"),
    # ("transactions_to_vessel_before_details.json", "ts_transactions_to_vessel_before_details"),
    # ("transactions_to_vessel_after_details.json", "ts_transactions_to_vessel_after_details"),
    ("transactions_additional_details.json", "ts_transactions_additional_details"),
    ("transactions_extraction_parcels.json", "ts_transactions_extraction_parcels"),
    # ("transactions_addition_ops.json", "ts_transactions_addition_ops"),
]
def main():
    for filename, table_name in ordered_table_files:
        pk_col = UPSERT_PK_MAP[table_name]
        path = os.path.join(DATA_DIR, filename)
        print(f"\nProcessing: {path} -> {table_name}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print("Loaded records from JSON:", len(data))
        print("First 3 records:", data[:3])
        df = pd.DataFrame(data)
        # PATCH: Always keep ts_docket as string for parcels table!
        if table_name == "ts_transactions_extraction_parcels" and "ts_docket" in df.columns:
            df["ts_docket"] = df["ts_docket"].astype(str)
        df = convert_epoch_columns(df)
        sql_col_max_lengths = get_varchar_lengths(engine, table_name)
        static_col_max_lengths = TS_TABLE_VARCHAR_LENGTHS.get(table_name, {})
        print(f"SQL schema max lengths for {table_name}: {sql_col_max_lengths}")
        print(f"Static mapping max lengths for {table_name}: {static_col_max_lengths}")
        df = trim_all_varchar_cols(df, sql_col_max_lengths, static_col_max_lengths)
        df = serialize_dict_columns(df)
        df = remove_reversed_records(df)
        # PATCH: Do NOT enforce pk type for string PKs like ts_docket
        if table_name != "ts_transactions_extraction_parcels":
            df = enforce_pk_types(df, pk_col)
        df = remove_null_pks(df, pk_col)
        df = deduplicate_dataframe(df, pk_col)
        print(df.dtypes)
        print(df.head())
        bulk_insert_records(df, table_name, engine, chunk_size=10000)
        print(f"Uploaded {len(df)} records to {table_name}.")

if __name__ == "__main__":
    main()