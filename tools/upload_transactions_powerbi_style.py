# vintrick-backend/tools/upload_transactions_powerbi_style.py
# Processes transaction files one by one from a folder, chunked upload, progress bar + ETA
# Excludes additionOps, analysisOps, additionalDetails

import pandas as pd
import json
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from tqdm import tqdm

# --- CONFIG ---
load_dotenv()
TRANSACTION_JSON_DIR = os.getenv("TRANSACTION_JSON_DIR", "Main/data/GET--transactions/")
DATABASE_URL = os.getenv("DB_URL") or os.getenv("DATABASE_URL")
TABLE_NAME = os.getenv("TRANSACTIONS_TABLE", "transactions_powerbi_style")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))  # Number of rows per batch

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set. Please add to .env or environment.")

def extract_flat_transaction(tx, file_date=None):
    # Exclude: additionOps, analysisOps, additionalDetails
    row = {
        "file_date": file_date,
        "formattedDate": tx.get("formattedDate"),
        "date": tx.get("date"),
        "operationId": tx.get("operationId"),
        "operationTypeId": tx.get("operationTypeId"),
        "operationTypeName": tx.get("operationTypeName"),
        "subOperationId": tx.get("subOperationId"),
        "subOperationTypeName": tx.get("subOperationTypeName"),
        "lastModified": tx.get("lastModified"),
        "reversed": tx.get("reversed"),
        "workorder": tx.get("workorder"),
        "jobNumber": tx.get("jobNumber"),
        "treatment": tx.get("treatment"),
        "assignedBy": tx.get("assignedBy"),
        "completedBy": tx.get("completedBy"),
        "winery": tx.get("winery"),
    }
    # fromVessel (flatten beforeDetails and afterDetails)
    fv = tx.get("fromVessel")
    if fv:
        row.update({
            "fromVessel_name": fv.get("name"),
            "fromVessel_id": fv.get("id"),
            "fromVessel_volOut": fv.get("volOut"),
            "fromVessel_volOutUnit": fv.get("volOutUnit"),
        })
        bd = fv.get("beforeDetails", {})
        ad = fv.get("afterDetails", {})
        for prefix, details in [("fromVessel_before", bd), ("fromVessel_after", ad)]:
            if details:
                row.update({
                    f"{prefix}_contentsId": details.get("contentsId"),
                    f"{prefix}_batch": details.get("batch"),
                    f"{prefix}_batchId": details.get("batchId"),
                    f"{prefix}_volume": details.get("volume"),
                    f"{prefix}_volumeUnit": details.get("volumeUnit"),
                    f"{prefix}_dip": details.get("dip"),
                    f"{prefix}_state": details.get("state"),
                    f"{prefix}_rawTaxClass": details.get("rawTaxClass"),
                    f"{prefix}_federalTaxClass": details.get("federalTaxClass"),
                    f"{prefix}_stateTaxClass": details.get("stateTaxClass"),
                    f"{prefix}_program": details.get("program"),
                    f"{prefix}_grading": details.get("grading"),
                    f"{prefix}_productCategory": details.get("productCategory"),
                    f"{prefix}_batchOwner": details.get("batchOwner"),
                    f"{prefix}_serviceOrder": details.get("serviceOrder"),
                    f"{prefix}_alcoholicFermentState": details.get("alcoholicFermentState"),
                    f"{prefix}_malolacticFermentState": details.get("malolacticFermentState"),
                    f"{prefix}_revisionName": details.get("revisionName"),
                    f"{prefix}_physicalStateText": details.get("physicalStateText"),
                })
                # batchDetails (nested)
                bdets = details.get("batchDetails", {})
                if bdets:
                    row.update({
                        f"{prefix}_batchDetails_id": bdets.get("id"),
                        f"{prefix}_batchDetails_name": bdets.get("name"),
                        f"{prefix}_batchDetails_description": bdets.get("description"),
                    })
                    # vintage, variety, region
                    for subkey in ["vintage", "variety", "region"]:
                        sub = bdets.get(subkey)
                        if sub:
                            row.update({
                                f"{prefix}_batchDetails_{subkey}_id": sub.get("id"),
                                f"{prefix}_batchDetails_{subkey}_name": sub.get("name"),
                                f"{prefix}_batchDetails_{subkey}_type": sub.get("type"),
                            })
    # toVessel (same flattening)
    tv = tx.get("toVessel")
    if tv:
        row.update({
            "toVessel_name": tv.get("name"),
            "toVessel_id": tv.get("id"),
            "toVessel_volIn": tv.get("volIn"),
            "toVessel_volInUnit": tv.get("volInUnit"),
        })
        bd = tv.get("beforeDetails", {})
        ad = tv.get("afterDetails", {})
        for prefix, details in [("toVessel_before", bd), ("toVessel_after", ad)]:
            if details:
                row.update({
                    f"{prefix}_contentsId": details.get("contentsId"),
                    f"{prefix}_batch": details.get("batch"),
                    f"{prefix}_batchId": details.get("batchId"),
                    f"{prefix}_volume": details.get("volume"),
                    f"{prefix}_volumeUnit": details.get("volumeUnit"),
                    f"{prefix}_dip": details.get("dip"),
                    f"{prefix}_state": details.get("state"),
                    f"{prefix}_rawTaxClass": details.get("rawTaxClass"),
                    f"{prefix}_federalTaxClass": details.get("federalTaxClass"),
                    f"{prefix}_stateTaxClass": details.get("stateTaxClass"),
                    f"{prefix}_program": details.get("program"),
                    f"{prefix}_grading": details.get("grading"),
                    f"{prefix}_productCategory": details.get("productCategory"),
                    f"{prefix}_batchOwner": details.get("batchOwner"),
                    f"{prefix}_serviceOrder": details.get("serviceOrder"),
                    f"{prefix}_alcoholicFermentState": details.get("alcoholicFermentState"),
                    f"{prefix}_malolacticFermentState": details.get("malolacticFermentState"),
                    f"{prefix}_revisionName": details.get("revisionName"),
                    f"{prefix}_physicalStateText": details.get("physicalStateText"),
                })
                bdets = details.get("batchDetails", {})
                if bdets:
                    row.update({
                        f"{prefix}_batchDetails_id": bdets.get("id"),
                        f"{prefix}_batchDetails_name": bdets.get("name"),
                        f"{prefix}_batchDetails_description": bdets.get("description"),
                    })
                    for subkey in ["vintage", "variety", "region"]:
                        sub = bdets.get(subkey)
                        if sub:
                            row.update({
                                f"{prefix}_batchDetails_{subkey}_id": sub.get("id"),
                                f"{prefix}_batchDetails_{subkey}_name": sub.get("name"),
                                f"{prefix}_batchDetails_{subkey}_type": sub.get("type"),
                            })
    # lossDetails
    loss = tx.get("lossDetails")
    if loss:
        row.update({
            "loss_volume": loss.get("volume"),
            "loss_volumeUnit": loss.get("volumeUnit"),
            "loss_reason": loss.get("reason"),
        })
    # subOperationTypeId
    row["subOperationTypeId"] = tx.get("subOperationTypeId")
    return row

def chunked_iterable(iterable, size):
    chunk = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk

engine = create_engine(DATABASE_URL)

def safe_to_sql(df, table_name, engine):
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False)
    except Exception as e:
        print("Upload failed:", e)
        print("DataFrame columns:", df.columns.tolist())
        print("Sample row:", df.iloc[0].to_dict())
        raise

# --- MAIN: PROCESS FILES ONE BY ONE ---
json_files = [f for f in sorted(os.listdir(TRANSACTION_JSON_DIR)) if f.endswith(".json")]
total_files = len(json_files)
total_transactions = 0

# First, count total transactions for ETA/progress
for fname in json_files:
    with open(os.path.join(TRANSACTION_JSON_DIR, fname), "r", encoding="utf-8") as f:
        data = json.load(f)
    total_transactions += len(data.get("transactionSummaries", []))

print(f"Found {total_files} files, {total_transactions} transactions. Starting upload.")

overall_progress = tqdm(total=total_transactions, desc="Overall Progress", unit="tx")

uploaded_count = 0
for file_idx, fname in enumerate(json_files, start=1):
    file_path = os.path.join(TRANSACTION_JSON_DIR, fname)
    file_date = fname.split(".")[0]
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    txs = data.get("transactionSummaries", [])
    tx_count = len(txs)
    if tx_count == 0:
        continue
    file_progress = tqdm(total=tx_count, desc=f"File {file_idx}/{total_files}: {fname}", unit="tx", leave=False)
    # Process chunks within this file
    for chunk in chunked_iterable((extract_flat_transaction(tx, file_date=file_date) for tx in txs), CHUNK_SIZE):
        df = pd.DataFrame(chunk)
        df.columns = [str(c).replace(' ', '_').replace('-', '_').replace('.', '__') for c in df.columns]
        safe_to_sql(df, TABLE_NAME, engine)
        uploaded_count += len(df)
        file_progress.update(len(df))
        overall_progress.update(len(df))
    file_progress.close()

overall_progress.close()
print(f"Upload complete! {uploaded_count} transactions uploaded.")

"""
How to use:
1. Set TRANSACTION_JSON_DIR, DB_URL (or DATABASE_URL), TRANSACTIONS_TABLE, and optionally CHUNK_SIZE in your .env or edit above.
2. Run: python vintrick-backend/tools/upload_transactions_powerbi_style.py
3. Progress bar and ETA will show for each file and overall upload.
"""