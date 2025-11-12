# python tools/upload_transactions_main_summary.py

import json
import os
from utils.helpers import safe_get

JSON_DIR = os.getenv("TRANSACTIONS_JSON", "Main/data/GET--transactions_by_day/")
OUT_DIR = os.getenv("TRANSACTIONS_SPLIT_DIR", "Main/data/GET--transactions_by_day/tables")
os.makedirs(OUT_DIR, exist_ok=True)

json_files = [
    os.path.join(JSON_DIR, fname)
    for fname in os.listdir(JSON_DIR)
    if fname.endswith(".json") and os.path.isfile(os.path.join(JSON_DIR, fname))
]

simple_table = []

for json_file in json_files:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "transactionSummaries" in data:
        transactions = data["transactionSummaries"]
    elif isinstance(data, list):
        transactions = data
    else:
        continue

    if not isinstance(transactions, list):
        continue

    for transaction in transactions:
        if not isinstance(transaction, dict):
            continue

        ts_subOperationId = safe_get(transaction.get("subOperationId"))
        ts_operationTypeId = safe_get(transaction.get("operationTypeId"))
        ts_subOperationTypeName = safe_get(transaction.get("subOperationTypeName"))
        ts_reversed = safe_get(transaction.get("reversed"))

        # From vessel
        from_vessel = safe_get(transaction.get("fromVessel"))
        from_name = safe_get(from_vessel.get("name")) if from_vessel else None
        from_id = safe_get(from_vessel.get("id")) if from_vessel else None
        from_volOut = safe_get(from_vessel.get("volOut")) if from_vessel else None
        from_before = safe_get(from_vessel.get("beforeDetails")) if from_vessel else None
        from_after = safe_get(from_vessel.get("afterDetails")) if from_vessel else None

        # To vessel
        to_vessel = safe_get(transaction.get("toVessel"))
        to_name = safe_get(to_vessel.get("name")) if to_vessel else None
        to_id = safe_get(to_vessel.get("id")) if to_vessel else None
        to_volIn = safe_get(to_vessel.get("volIn")) if to_vessel else None
        to_before = safe_get(to_vessel.get("beforeDetails")) if to_vessel else None
        to_after = safe_get(to_vessel.get("afterDetails")) if to_vessel else None

        # Loss details
        loss_details = safe_get(transaction.get("lossDetails"))

        # Calculate extra columns
        from_before_volume = safe_get(from_before.get("volume")) if from_before else None
        from_after_volume = safe_get(from_after.get("volume")) if from_after else None
        to_before_volume = safe_get(to_before.get("volume")) if to_before else None
        to_after_volume = safe_get(to_after.get("volume")) if to_after else None

        # Compute movements (handle None)
        def safe_minus(a, b):
            a = float(a) if a is not None else 0.0
            b = float(b) if b is not None else 0.0
            return a - b

        from_vessel_moved = safe_minus(from_before_volume, from_after_volume)
        to_vessel_moved = safe_minus(to_before_volume, to_after_volume)

        row = {
            # Transaction fields
            "ts_subOperationId": ts_subOperationId,
            "ts_operationId": safe_get(transaction.get("operationId")),
            "ts_operationTypeId": ts_operationTypeId,
            "ts_operationTypeName": safe_get(transaction.get("operationTypeName")),
            "ts_subOperationTypeName": ts_subOperationTypeName,
            "ts_formattedDate": safe_get(transaction.get("formattedDate")),
            "ts_date": safe_get(transaction.get("date")),
            "ts_lastModified": safe_get(transaction.get("lastModified")),
            "ts_reversed": ts_reversed,
            "ts_workorder": safe_get(transaction.get("workorder")),
            "ts_jobNumber": safe_get(transaction.get("jobNumber")),
            "ts_treatment": safe_get(transaction.get("treatment")),
            "ts_assignedBy": safe_get(transaction.get("assignedBy")),
            "ts_completedBy": safe_get(transaction.get("completedBy")),
            "ts_winery": safe_get(transaction.get("winery")),

            # From vessel
            "from_ts_name": from_name,
            "from_ts_vessel_id": from_id,
            "from_ts_volOut": from_volOut,
            "from_before_contentsId": safe_get(from_before.get("contentsId")) if from_before else None,
            "from_before_batch": safe_get(from_before.get("batch")) if from_before else None,
            "from_before_batchId": safe_get(from_before.get("batchId")) if from_before else None,
            "from_before_volume": from_before_volume,
            "from_after_contentsId": safe_get(from_after.get("contentsId")) if from_after else None,
            "from_after_batch": safe_get(from_after.get("batch")) if from_after else None,
            "from_after_batchId": safe_get(from_after.get("batchId")) if from_after else None,
            "from_after_volume": from_after_volume,

            # To vessel
            "to_ts_name": to_name,
            "to_ts_vessel_id": to_id,
            "to_ts_volIn": to_volIn,
            "to_before_contentsId": safe_get(to_before.get("contentsId")) if to_before else None,
            "to_before_batch": safe_get(to_before.get("batch")) if to_before else None,
            "to_before_batchId": safe_get(to_before.get("batchId")) if to_before else None,
            "to_before_volume": to_before_volume,
            "to_after_contentsId": safe_get(to_after.get("contentsId")) if to_after else None,
            "to_after_batch": safe_get(to_after.get("batch")) if to_after else None,
            "to_after_batchId": safe_get(to_after.get("batchId")) if to_after else None,
            "to_after_volume": to_after_volume,

            # Loss details
            "loss_volume": safe_get(loss_details.get("volume")) if loss_details else None,
            "loss_volumeUnit": safe_get(loss_details.get("volumeUnit")) if loss_details else None,
            "loss_reason": safe_get(loss_details.get("reason")) if loss_details else None,

            # New columns
            "from_vessel_moved": from_vessel_moved,
            "to_vessel_moved": to_vessel_moved,
        }
        simple_table.append(row)

with open(os.path.join(OUT_DIR, "ts_transactions_simple_table.json"), "w", encoding="utf-8") as f:
    json.dump(simple_table, f, indent=2, ensure_ascii=False)

print("Simple table complete! Written to", os.path.join(OUT_DIR, "ts_transactions_simple_table.json"))