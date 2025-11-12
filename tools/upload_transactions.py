# python tools/upload_transactions.py

import json
import os
import uuid

from utils.helpers import safe_get_path, safe_get

# Directory containing all JSON files to process
JSON_DIR = os.getenv("TRANSACTIONS_JSON", "Main/data/GET--transactions_by_day/")
# Directory to write split tables
OUT_DIR = os.getenv("TRANSACTIONS_SPLIT_DIR", "Main/data/GET--transactions_by_day/tables")
os.makedirs(OUT_DIR, exist_ok=True)

def generate_uid():
    return str(uuid.uuid4())

# Find all .json files in JSON_DIR, but NOT in OUT_DIR or subdirectories
json_files = [
    os.path.join(JSON_DIR, fname)
    for fname in os.listdir(JSON_DIR)
    if fname.endswith(".json") and os.path.isfile(os.path.join(JSON_DIR, fname))
]

print(f"Found {len(json_files)} files to process in {JSON_DIR} (not going into {OUT_DIR}).")

# Accumulate all tables from all files
transactions_table = []
transactions_from_vessel_table = []
transactions_from_vessel_before_details_table = []
transactions_from_vessel_after_details_table = []
transactions_to_vessel_table = []
transactions_to_vessel_before_details_table = []
transactions_to_vessel_after_details_table = []
transactions_loss_details_table = []
transactions_analysis_ops_table = []
transactions_metrics_table = []

for json_file in json_files:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle wrapped or direct format
    if isinstance(data, dict) and "transactionSummaries" in data:
        transactions = data["transactionSummaries"]
    elif isinstance(data, list):
        transactions = data
    else:
        print(f"WARNING: {json_file} is not a valid transactions file, skipping.")
        continue

    for transaction in transactions:
        if not isinstance(transaction, dict):
            print(f"SKIPPING: Found transaction that's not a dict in file {json_file}: {repr(transaction)}")
            continue
        # ... rest of your logic ...

        ts_id = generate_uid()
        # --- Transactions Table ---
        transaction_row = {
            "ts_id": ts_id,
            "ts_operationId": safe_get(transaction.get("operationId")),
            "ts_operationTypeId": safe_get(transaction.get("operationTypeId")),
            "ts_operationTypeName": safe_get(transaction.get("operationTypeName")),
            "ts_subOperationId": safe_get(transaction.get("subOperationId")),
            "ts_subOperationTypeName": safe_get(transaction.get("subOperationTypeName")),
            "ts_formattedDate": safe_get(transaction.get("formattedDate")),
            "ts_date": safe_get(transaction.get("date")),
            "ts_lastModified": safe_get(transaction.get("lastModified")),
            "ts_reversed": safe_get(transaction.get("reversed")),
            "ts_workorder": safe_get(transaction.get("workorder")),
            "ts_jobNumber": safe_get(transaction.get("jobNumber")),
            "ts_treatment": safe_get(transaction.get("treatment")),
            "ts_assignedBy": safe_get(transaction.get("assignedBy")),
            "ts_completedBy": safe_get(transaction.get("completedBy")),
            "ts_winery": safe_get(transaction.get("winery")),
            "ts_subOperationTypeId": safe_get(transaction.get("subOperationTypeId")),
        }
        transactions_table.append(transaction_row)

        # --- From Vessel Table ---
        from_vessel = safe_get(transaction.get("fromVessel"))
        if from_vessel:
            ts_from_vessel_id = generate_uid()
            transaction_row["ts_from_vessel_id"] = ts_from_vessel_id
            from_vessel_row = {
                "ts_from_vessel_id": ts_from_vessel_id,
                "ts_id": ts_id,
                "ts_name": safe_get(from_vessel.get("name")),
                "ts_vessel_id": safe_get(from_vessel.get("id")),
                "ts_volOut": safe_get(from_vessel.get("volOut")),
                "ts_volOutUnit": safe_get(from_vessel.get("volOutUnit")),
            }
            transactions_from_vessel_table.append(from_vessel_row)

            # --- Before Details Table ---
            before_details = safe_get(from_vessel.get("beforeDetails"))
            if before_details:
                ts_before_details_id = generate_uid()
                from_vessel_row["ts_before_details_id"] = ts_before_details_id
                before_details_row = {
                    "ts_before_details_id": ts_before_details_id,
                    "ts_from_vessel_id": ts_from_vessel_id,
                    "ts_contentsId": safe_get(before_details.get("contentsId")),
                    "ts_batch": safe_get(before_details.get("batch")),
                    "ts_batchId": safe_get(before_details.get("batchId")),
                    "ts_volume": safe_get(before_details.get("volume")),
                    "ts_volumeUnit": safe_get(before_details.get("volumeUnit")),
                    "ts_dip": safe_get(before_details.get("dip")),
                    "ts_state": safe_get(before_details.get("state")),
                    "ts_rawTaxClass": safe_get(before_details.get("rawTaxClass")),
                    "ts_federalTaxClass": safe_get(before_details.get("federalTaxClass")),
                    "ts_stateTaxClass": safe_get(before_details.get("stateTaxClass")),
                    "ts_program": safe_get(before_details.get("program")),
                    "ts_grading": safe_get(before_details.get("grading")),
                    "ts_productCategory": safe_get(before_details.get("productCategory")),
                    "ts_batchOwner": safe_get(before_details.get("batchOwner")),
                    "ts_serviceOrder": safe_get(before_details.get("serviceOrder")),
                    "ts_alcoholicFermentState": safe_get(before_details.get("alcoholicFermentState")),
                    "ts_malolacticFermentState": safe_get(before_details.get("malolacticFermentState")),
                    "ts_revisionName": safe_get(before_details.get("revisionName")),
                    "ts_physicalStateText": safe_get(before_details.get("physicalStateText")),
                    "ts_batchDetails_id": None,
                }
                batch_details = safe_get(before_details.get("batchDetails"))
                if batch_details:
                    ts_batchDetails_id = generate_uid()
                    before_details_row["ts_batchDetails_id"] = ts_batchDetails_id
                    before_details_row.update({
                        "ts_batchDetails_id": ts_batchDetails_id,
                        "ts_batchDetails_name": safe_get(batch_details.get("name")),
                        "ts_batchDetails_description": safe_get(batch_details.get("description")),
                        "ts_batchDetails_vintage_id": safe_get_path(batch_details, ["vintage", "id"]),
                        "ts_batchDetails_vintage_name": safe_get_path(batch_details, ["vintage", "name"]),
                        "ts_batchDetails_variety_id": safe_get_path(batch_details, ["variety", "id"]),
                        "ts_batchDetails_variety_name": safe_get_path(batch_details, ["variety", "name"]),
                        "ts_batchDetails_region_id": safe_get_path(batch_details, ["region", "id"]),
                        "ts_batchDetails_region_name": safe_get_path(batch_details, ["region", "name"]),
                    })
                transactions_from_vessel_before_details_table.append(before_details_row)

            # --- After Details Table ---
            after_details = safe_get(from_vessel.get("afterDetails"))
            if after_details:
                ts_after_details_id = generate_uid()
                from_vessel_row["ts_after_details_id"] = ts_after_details_id
                after_details_row = {
                    "ts_after_details_id": ts_after_details_id,
                    "ts_from_vessel_id": ts_from_vessel_id,
                    "ts_contentsId": safe_get(after_details.get("contentsId")),
                    "ts_batch": safe_get(after_details.get("batch")),
                    "ts_batchId": safe_get(after_details.get("batchId")),
                    "ts_volume": safe_get(after_details.get("volume")),
                    "ts_volumeUnit": safe_get(after_details.get("volumeUnit")),
                    "ts_dip": safe_get(after_details.get("dip")),
                    "ts_state": safe_get(after_details.get("state")),
                    "ts_rawTaxClass": safe_get(after_details.get("rawTaxClass")),
                    "ts_federalTaxClass": safe_get(after_details.get("federalTaxClass")),
                    "ts_stateTaxClass": safe_get(after_details.get("stateTaxClass")),
                    "ts_program": safe_get(after_details.get("program")),
                    "ts_grading": safe_get(after_details.get("grading")),
                    "ts_productCategory": safe_get(after_details.get("productCategory")),
                    "ts_batchOwner": safe_get(after_details.get("batchOwner")),
                    "ts_serviceOrder": safe_get(after_details.get("serviceOrder")),
                    "ts_alcoholicFermentState": safe_get(after_details.get("alcoholicFermentState")),
                    "ts_malolacticFermentState": safe_get(after_details.get("malolacticFermentState")),
                    "ts_revisionName": safe_get(after_details.get("revisionName")),
                    "ts_physicalStateText": safe_get(after_details.get("physicalStateText")),
                    "ts_batchDetails_id": None,
                }
                batch_details = safe_get(after_details.get("batchDetails"))
                if batch_details:
                    ts_batchDetails_id = generate_uid()
                    after_details_row["ts_batchDetails_id"] = ts_batchDetails_id
                    after_details_row.update({
                        "ts_batchDetails_id": ts_batchDetails_id,
                        "ts_batchDetails_name": safe_get(batch_details.get("name")),
                        "ts_batchDetails_description": safe_get(batch_details.get("description")),
                        "ts_batchDetails_vintage_id": safe_get_path(batch_details, ["vintage", "id"]),
                        "ts_batchDetails_vintage_name": safe_get_path(batch_details, ["vintage", "name"]),
                        "ts_batchDetails_variety_id": safe_get_path(batch_details, ["variety", "id"]),
                        "ts_batchDetails_variety_name": safe_get_path(batch_details, ["variety", "name"]),
                        "ts_batchDetails_region_id": safe_get_path(batch_details, ["region", "id"]),
                        "ts_batchDetails_region_name": safe_get_path(batch_details, ["region", "name"]),
                    })
                transactions_from_vessel_after_details_table.append(after_details_row)

        # --- To Vessel Table ---
        to_vessel = safe_get(transaction.get("toVessel"))
        if to_vessel:
            ts_to_vessel_id = generate_uid()
            transaction_row["ts_to_vessel_id"] = ts_to_vessel_id
            to_vessel_row = {
                "ts_to_vessel_id": ts_to_vessel_id,
                "ts_id": ts_id,
                "ts_name": safe_get(to_vessel.get("name")),
                "ts_vessel_id": safe_get(to_vessel.get("id")),
                "ts_volIn": safe_get(to_vessel.get("volIn")),
                "ts_volInUnit": safe_get(to_vessel.get("volInUnit")),
            }
            transactions_to_vessel_table.append(to_vessel_row)

            # --- Before Details Table ---
            before_details = safe_get(to_vessel.get("beforeDetails"))
            if before_details:
                ts_before_details_id = generate_uid()
                to_vessel_row["ts_before_details_id"] = ts_before_details_id
                before_details_row = {
                    "ts_before_details_id": ts_before_details_id,
                    "ts_to_vessel_id": ts_to_vessel_id,
                    "ts_contentsId": safe_get(before_details.get("contentsId")),
                    "ts_batch": safe_get(before_details.get("batch")),
                    "ts_batchId": safe_get(before_details.get("batchId")),
                    "ts_volume": safe_get(before_details.get("volume")),
                    "ts_volumeUnit": safe_get(before_details.get("volumeUnit")),
                    "ts_dip": safe_get(before_details.get("dip")),
                    "ts_state": safe_get(before_details.get("state")),
                    "ts_rawTaxClass": safe_get(before_details.get("rawTaxClass")),
                    "ts_federalTaxClass": safe_get(before_details.get("federalTaxClass")),
                    "ts_stateTaxClass": safe_get(before_details.get("stateTaxClass")),
                    "ts_program": safe_get(before_details.get("program")),
                    "ts_grading": safe_get(before_details.get("grading")),
                    "ts_productCategory": safe_get(before_details.get("productCategory")),
                    "ts_batchOwner": safe_get(before_details.get("batchOwner")),
                    "ts_serviceOrder": safe_get(before_details.get("serviceOrder")),
                    "ts_alcoholicFermentState": safe_get(before_details.get("alcoholicFermentState")),
                    "ts_malolacticFermentState": safe_get(before_details.get("malolacticFermentState")),
                    "ts_revisionName": safe_get(before_details.get("revisionName")),
                    "ts_physicalStateText": safe_get(before_details.get("physicalStateText")),
                    "ts_batchDetails_id": None,
                }
                batch_details = safe_get(before_details.get("batchDetails"))
                if batch_details:
                    ts_batchDetails_id = generate_uid()
                    before_details_row["ts_batchDetails_id"] = ts_batchDetails_id
                    before_details_row.update({
                        "ts_batchDetails_id": ts_batchDetails_id,
                        "ts_batchDetails_name": safe_get(batch_details.get("name")),
                        "ts_batchDetails_description": safe_get(batch_details.get("description")),
                        "ts_batchDetails_vintage_id": safe_get_path(batch_details, ["vintage", "id"]),
                        "ts_batchDetails_vintage_name": safe_get_path(batch_details, ["vintage", "name"]),
                        "ts_batchDetails_variety_id": safe_get_path(batch_details, ["variety", "id"]),
                        "ts_batchDetails_variety_name": safe_get_path(batch_details, ["variety", "name"]),
                        "ts_batchDetails_region_id": safe_get_path(batch_details, ["region", "id"]),
                        "ts_batchDetails_region_name": safe_get_path(batch_details, ["region", "name"]),
                    })
                transactions_to_vessel_before_details_table.append(before_details_row)

            # --- After Details Table ---
            after_details = safe_get(to_vessel.get("afterDetails"))
            if after_details:
                ts_after_details_id = generate_uid()
                to_vessel_row["ts_after_details_id"] = ts_after_details_id
                after_details_row = {
                    "ts_after_details_id": ts_after_details_id,
                    "ts_to_vessel_id": ts_to_vessel_id,
                    "ts_contentsId": safe_get(after_details.get("contentsId")),
                    "ts_batch": safe_get(after_details.get("batch")),
                    "ts_batchId": safe_get(after_details.get("batchId")),
                    "ts_volume": safe_get(after_details.get("volume")),
                    "ts_volumeUnit": safe_get(after_details.get("volumeUnit")),
                    "ts_dip": safe_get(after_details.get("dip")),
                    "ts_state": safe_get(after_details.get("state")),
                    "ts_rawTaxClass": safe_get(after_details.get("rawTaxClass")),
                    "ts_federalTaxClass": safe_get(after_details.get("federalTaxClass")),
                    "ts_stateTaxClass": safe_get(after_details.get("stateTaxClass")),
                    "ts_program": safe_get(after_details.get("program")),
                    "ts_grading": safe_get(after_details.get("grading")),
                    "ts_productCategory": safe_get(after_details.get("productCategory")),
                    "ts_batchOwner": safe_get(after_details.get("batchOwner")),
                    "ts_serviceOrder": safe_get(after_details.get("serviceOrder")),
                    "ts_alcoholicFermentState": safe_get(after_details.get("alcoholicFermentState")),
                    "ts_malolacticFermentState": safe_get(after_details.get("malolacticFermentState")),
                    "ts_revisionName": safe_get(after_details.get("revisionName")),
                    "ts_physicalStateText": safe_get(after_details.get("physicalStateText")),
                    "ts_batchDetails_id": None,
                }
                batch_details = safe_get(after_details.get("batchDetails"))
                if batch_details:
                    ts_batchDetails_id = generate_uid()
                    after_details_row["ts_batchDetails_id"] = ts_batchDetails_id
                    after_details_row.update({
                        "ts_batchDetails_id": ts_batchDetails_id,
                        "ts_batchDetails_name": safe_get(batch_details.get("name")),
                        "ts_batchDetails_description": safe_get(batch_details.get("description")),
                        "ts_batchDetails_vintage_id": safe_get_path(batch_details, ["vintage", "id"]),
                        "ts_batchDetails_vintage_name": safe_get_path(batch_details, ["vintage", "name"]),
                        "ts_batchDetails_variety_id": safe_get_path(batch_details, ["variety", "id"]),
                        "ts_batchDetails_variety_name": safe_get_path(batch_details, ["variety", "name"]),
                        "ts_batchDetails_region_id": safe_get_path(batch_details, ["region", "id"]),
                        "ts_batchDetails_region_name": safe_get_path(batch_details, ["region", "name"]),
                    })
                transactions_to_vessel_after_details_table.append(after_details_row)

        # --- Loss Details Table ---
        loss_details = safe_get(transaction.get("lossDetails"))
        if loss_details:
            ts_loss_details_id = generate_uid()
            transaction_row["ts_loss_details_id"] = ts_loss_details_id
            loss_details_row = {
                "ts_loss_details_id": ts_loss_details_id,
                "ts_id": ts_id,
                "ts_volume": safe_get(loss_details.get("volume")),
                "ts_volumeUnit": safe_get(loss_details.get("volumeUnit")),
                "ts_reason": safe_get(loss_details.get("reason")),
            }
            transactions_loss_details_table.append(loss_details_row)

        # --- Analysis Ops Table ---
        analysis_ops = safe_get(transaction.get("analysisOps"))
        if analysis_ops:
            ts_analysis_ops_id = generate_uid()
            transaction_row["ts_analysis_ops_id"] = ts_analysis_ops_id
            analysis_ops_row = {
                "ts_analysis_ops_id": ts_analysis_ops_id,
                "ts_id": ts_id,
                "ts_vesselId": safe_get(analysis_ops.get("vesselId")),
                "ts_vesselName": safe_get(analysis_ops.get("vesselName")),
                "ts_batchId": safe_get(analysis_ops.get("batchId")),
                "ts_batchName": safe_get(analysis_ops.get("batchName")),
                "ts_templateId": safe_get(analysis_ops.get("templateId")),
                "ts_templateName": safe_get(analysis_ops.get("templateName")),
            }
            transactions_analysis_ops_table.append(analysis_ops_row)

            # --- Metrics Table (inside analysisOps) ---
            metrics = safe_get(analysis_ops.get("metrics")) or []
            for metric in metrics:
                ts_metrics_id = generate_uid()
                metric_row = {
                    "ts_metrics_id": ts_metrics_id,
                    "ts_analysis_ops_id": ts_analysis_ops_id,
                    "ts_id": ts_id,
                    "ts_metric_id": safe_get(metric.get("id")),
                    "ts_metric_name": safe_get(metric.get("name")),
                    "ts_metric_value": safe_get(metric.get("value")),
                    "ts_metric_txtValue": safe_get(metric.get("txtValue")),
                    "ts_metric_unit": safe_get(metric.get("unit")),
                }
                transactions_metrics_table.append(metric_row)

# --- Write to JSON files ---
with open(os.path.join(OUT_DIR, "transactions.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_table, f, indent=2)

with open(os.path.join(OUT_DIR, "transactions_from_vessel.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_from_vessel_table, f, indent=2)

with open(os.path.join(OUT_DIR, "transactions_from_vessel_before_details.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_from_vessel_before_details_table, f, indent=2)

with open(os.path.join(OUT_DIR, "transactions_from_vessel_after_details.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_from_vessel_after_details_table, f, indent=2)

with open(os.path.join(OUT_DIR, "transactions_to_vessel.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_to_vessel_table, f, indent=2)

with open(os.path.join(OUT_DIR, "transactions_to_vessel_before_details.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_to_vessel_before_details_table, f, indent=2)

with open(os.path.join(OUT_DIR, "transactions_to_vessel_after_details.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_to_vessel_after_details_table, f, indent=2)

with open(os.path.join(OUT_DIR, "transactions_loss_details.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_loss_details_table, f, indent=2)

with open(os.path.join(OUT_DIR, "transactions_analysis_ops.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_analysis_ops_table, f, indent=2)

with open(os.path.join(OUT_DIR, "transactions_metrics.json"), "w", encoding="utf-8") as f:
    json.dump(transactions_metrics_table, f, indent=2)

print("Split complete! JSON tables written to", OUT_DIR)