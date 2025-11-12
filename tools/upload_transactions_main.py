# python tools/upload_transactions_main.py

import json
import os
import pandas as pd
from collections import defaultdict
from utils.helpers import safe_get_path, safe_get

JSON_DIR = os.getenv("TRANSACTIONS_JSON", "Main/data/GET--transactions_by_day/")
OUT_DIR = os.getenv("TRANSACTIONS_SPLIT_DIR", "Main/data/GET--transactions_by_day/tables")
ID_OUT_DIR = "Main/data/id_tables"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ID_OUT_DIR, exist_ok=True)

json_files = [
    os.path.join(JSON_DIR, fname)
    for fname in os.listdir(JSON_DIR)
    if fname.endswith(".json") and os.path.isfile(os.path.join(JSON_DIR, fname))
]

print(f"Found {len(json_files)} files to process in {JSON_DIR} (not going into {OUT_DIR}).")

MAX_LENGTHS = {
    "transactions_additional_details": {
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
        "ts_press": 50
    },
}

def get_docket_keys(row, key="ts_dockets"):
    dockets_val = row.get(key, "")
    if isinstance(dockets_val, list):
        return [str(d).strip() for d in dockets_val if str(d).strip()]
    return [d.strip() for d in str(dockets_val).split(",") if d.strip()]

def safe_json_dump(data, file):
    if isinstance(data, pd.DataFrame):
        data = data.where(pd.notnull(data), None)
        data = data.to_dict(orient="records")
    elif isinstance(data, list):
        data = [
            {k: (None if pd.isnull(v) else v) for k, v in row.items()}
            for row in data
        ]
    json.dump(data, file, indent=2, ensure_ascii=False)

def normalize_additional_details_table(details_rows):
    import pandas as pd
    df = pd.DataFrame(details_rows)
    grouped_rows = df[df['ts_dockets'].fillna('').str.contains(',')].copy()
    docket_info = {}
    for _, row in grouped_rows.iterrows():
        dockets = [d.strip() for d in str(row['ts_dockets']).split(',')]
        for docket in dockets:
            if docket not in docket_info:
                docket_info[docket] = {}
            for col in df.columns:
                val = row[col]
                if pd.notnull(val) and str(val).upper() != 'NULL':
                    docket_info[docket][col] = val
    for idx, row in df.iterrows():
        dockets = [d.strip() for d in str(row['ts_dockets']).split(',')]
        if len(dockets) == 1 and dockets[0] in docket_info:
            docket = dockets[0]
            for col in df.columns:
                if (pd.isnull(row[col]) or str(row[col]).upper() == 'NULL') and col in docket_info[docket]:
                    df.at[idx, col] = docket_info[docket][col]
    return df.to_dict(orient="records")

def flatten_value(val):
    if isinstance(val, list):
        return ",".join(map(str, val))
    return val

def trim_row(row, max_lengths):
    for key, maxlen in max_lengths.items():
        val = row.get(key)
        if isinstance(val, str) and maxlen is not None:
            row[key] = val[:maxlen]
    return row

# Tables with ts_ prefix
ts_transactions_table = []
ts_transactions_from_vessel_table = []
ts_transactions_from_vessel_before_details_table = []
ts_transactions_from_vessel_after_details_table = []
ts_transactions_to_vessel_table = []
ts_transactions_to_vessel_before_details_table = []
ts_transactions_to_vessel_after_details_table = []
ts_transactions_loss_details_table = []
ts_transactions_analysis_metrics_table = []
ts_transactions_additional_details_table = []
ts_transactions_extraction_parcels_table = []
ts_transactions_addition_ops_table = []
ts_extraction_table = []
ts_grape_intake_table = []

# NEW: Transfer Operations Table
ts_transfer_operations_table = []

# Lookup tables for child entities
ts_batchDetails_vintage_table = {}
ts_batchDetails_variety_table = {}
ts_batchDetails_region_table = {}

from_vessel_seen_ids = set()
from_vessel_before_details_seen_ids = set()
from_vessel_after_details_seen_ids = set()
to_vessel_seen_ids = set()
to_vessel_before_details_seen_ids = set()
to_vessel_after_details_seen_ids = set()
loss_details_seen_ids = set()
additional_details_seen_ids = set()
addition_ops_seen_ids = set()
analysis_metrics_seen_keys = set()
extraction_parcels_seen_dockets = set()

special_transfer_table = []
special_transfer_from_intransit_table = []
special_transfer_intransit_to_intransit_table = []
special_transfer_link_table = []
# --- Load Tanks_All.json for In-Transit vessel lookup ---
with open("Main/data/id_tables/Tanks_All.json", "r", encoding="utf-8") as tank_file:
    tanks_all = json.load(tank_file)

tanks_lookup = {safe_get(tank.get("vessel")): safe_get(tank.get("Winery Building")) for tank in tanks_all}



# --- REFACTOR: Complete subOperationId mapping including nested parcels ---
all_transactions_by_subOp = {}
for json_file in json_files:
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "transactionSummaries" in data:
        transactions = data["transactionSummaries"]
    elif isinstance(data, list):
        transactions = data
    else:
        print(f"WARNING: {json_file} is not a valid transactions file, skipping.")
        continue

    if not isinstance(transactions, list):
        print(f"WARNING: Skipping file {json_file} because it does not contain a list of transactions.")
        continue

    for transaction in transactions:
        if not isinstance(transaction, dict):
            print(f"SKIPPING: Found transaction that's not a dict in file {json_file}: {repr(transaction)}")
            continue

        ts_subOperationId = safe_get(transaction.get("subOperationId"))
        if ts_subOperationId is not None:
            all_transactions_by_subOp[ts_subOperationId] = transaction

        # --- Scan additionalDetails/extraction for parcel subOperationIds ---
        additional_details = safe_get(transaction.get("additionalDetails"))
        if additional_details:
            extraction = safe_get(additional_details.get("extraction"))
            if extraction:
                for parcel in extraction.get("parcels", []):
                    parcel_sub_op_id = safe_get(parcel.get("subOperationId"))
                    if parcel_sub_op_id and parcel_sub_op_id not in all_transactions_by_subOp:
                        all_transactions_by_subOp[parcel_sub_op_id] = {
                            "parcel_context": parcel,
                            "parent_transaction": transaction
                        }
        # --- END REFACTOR ---

        ts_reversed = safe_get(transaction.get("reversed"))
        if ts_reversed is True or ts_reversed == "true":
            continue

        ts_operationTypeId = safe_get(transaction.get("operationTypeId"))
        ts_subOperationTypeName = safe_get(transaction.get("subOperationTypeName"))

        transaction_row = {
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
        }
        ts_transactions_table.append(transaction_row)

        # --- Collect Transfer Operations ---
        if ts_operationTypeId == 31 and ts_subOperationTypeName == "Transfer":
            transfer_row = {
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
            }
            ts_transfer_operations_table.append(transfer_row)

        from_vessel = safe_get(transaction.get("fromVessel"))
        to_vessel = safe_get(transaction.get("toVessel"))

        # --- Special transfer TO In-Transit-Bldg ---
        if (
            ts_operationTypeId == 47
            and to_vessel
            and safe_get(to_vessel.get("name"))
            and tanks_lookup.get(safe_get(to_vessel.get("name"))) == "In-Transit-Bldg"
        ):
            special_row = {
                "ts_subOperationId": ts_subOperationId,
                "ts_operationId": safe_get(transaction.get("operationId")),
                "ts_operationTypeId": ts_operationTypeId,
                "ts_operationTypeName": safe_get(transaction.get("operationTypeName")),
                "ts_subOperationTypeName": ts_subOperationTypeName,
                "ts_formattedDate": safe_get(transaction.get("formattedDate")),
                # From vessel fields
                "from_ts_name": safe_get(from_vessel.get("name")) if from_vessel else None,
                "from_ts_vessel_id": safe_get(from_vessel.get("id")) if from_vessel else None,
                "from_ts_volOut": safe_get(from_vessel.get("volOut")) if from_vessel else None,
                "from_ts_volOutUnit": safe_get(from_vessel.get("volOutUnit")) if from_vessel else None,
                # To vessel fields
                "to_ts_name": safe_get(to_vessel.get("name")),
                "to_ts_vessel_id": safe_get(to_vessel.get("id")),
                "to_ts_volIn": safe_get(to_vessel.get("volIn")),
                "to_ts_volInUnit": safe_get(to_vessel.get("volInUnit")),
            }
            special_transfer_table.append(special_row)

        # --- Special transfer FROM In-Transit-Bldg TO NOT In-Transit-Bldg ---
        if (
            from_vessel
            and safe_get(from_vessel.get("name")) in tanks_lookup
            and tanks_lookup.get(safe_get(from_vessel.get("name"))) == "In-Transit-Bldg"
            and to_vessel
            and safe_get(to_vessel.get("name")) in tanks_lookup
            and tanks_lookup.get(safe_get(to_vessel.get("name"))) != "In-Transit-Bldg"
        ):
            special_from_row = {
                "ts_subOperationId": ts_subOperationId,
                "ts_operationId": safe_get(transaction.get("operationId")),
                "ts_operationTypeId": ts_operationTypeId,
                "ts_operationTypeName": safe_get(transaction.get("operationTypeName")),
                "ts_subOperationTypeName": ts_subOperationTypeName,
                "ts_formattedDate": safe_get(transaction.get("formattedDate")),
                # From vessel fields
                "from_ts_name": safe_get(from_vessel.get("name")),
                "from_ts_vessel_id": safe_get(from_vessel.get("id")),
                "from_ts_volOut": safe_get(from_vessel.get("volOut")),
                "from_ts_volOutUnit": safe_get(from_vessel.get("volOutUnit")),
                # To vessel fields
                "to_ts_name": safe_get(to_vessel.get("name")),
                "to_ts_vessel_id": safe_get(to_vessel.get("id")),
                "to_ts_volIn": safe_get(to_vessel.get("volIn")),
                "to_ts_volInUnit": safe_get(to_vessel.get("volInUnit")),
            }
            special_transfer_from_intransit_table.append(special_from_row)

        # --- NEW: Special transfer FROM In-Transit-Bldg TO In-Transit-Bldg ---
        if (
            from_vessel
            and safe_get(from_vessel.get("name")) in tanks_lookup
            and tanks_lookup.get(safe_get(from_vessel.get("name"))) == "In-Transit-Bldg"
            and to_vessel
            and safe_get(to_vessel.get("name")) in tanks_lookup
            and tanks_lookup.get(safe_get(to_vessel.get("name"))) == "In-Transit-Bldg"
        ):
            special_intransit_row = {
                "ts_subOperationId": ts_subOperationId,
                "ts_operationId": safe_get(transaction.get("operationId")),
                "ts_operationTypeId": ts_operationTypeId,
                "ts_operationTypeName": safe_get(transaction.get("operationTypeName")),
                "ts_subOperationTypeName": ts_subOperationTypeName,
                "ts_formattedDate": safe_get(transaction.get("formattedDate")),
                # From vessel fields
                "from_ts_name": safe_get(from_vessel.get("name")),
                "from_ts_vessel_id": safe_get(from_vessel.get("id")),
                "from_ts_volOut": safe_get(from_vessel.get("volOut")),
                "from_ts_volOutUnit": safe_get(from_vessel.get("volOutUnit")),
                # To vessel fields
                "to_ts_name": safe_get(to_vessel.get("name")),
                "to_ts_vessel_id": safe_get(to_vessel.get("id")),
                "to_ts_volIn": safe_get(to_vessel.get("volIn")),
                "to_ts_volInUnit": safe_get(to_vessel.get("volInUnit")),
            }
            special_transfer_intransit_to_intransit_table.append(special_intransit_row)

            # After both special_transfer_table and special_transfer_from_intransit_table are populated

            # Build index for fast lookup on from_intransit
            from_intransit_index = {}
            for idx, row in enumerate(special_transfer_from_intransit_table):
                key = (row.get("from_ts_name"), row.get("from_ts_volOut"))
                from_intransit_index.setdefault(key, []).append((idx, row))

            # Now, scan the "to" in special_transfer_table and match against "from" in special_transfer_from_intransit_table
            for idx_to, to_row in enumerate(special_transfer_table):
                key = (to_row.get("to_ts_name"), to_row.get("to_ts_volIn"))
                matches = from_intransit_index.get(key, [])
                for idx_from, from_row in matches:
                    # Build the link (you can add more fields if you want)
                    link_row = {
                        "special_transfer_table_idx": idx_to,
                        "special_transfer_table_subOperationId": to_row.get("ts_subOperationId"),
                        "special_transfer_from_intransit_table_idx": idx_from,
                        "special_transfer_from_intransit_table_subOperationId": from_row.get("ts_subOperationId"),
                        "vessel_name": key[0],
                        "volume": key[1]
                    }
                    special_transfer_link_table.append(link_row)


        if from_vessel:
            if ts_subOperationId not in from_vessel_seen_ids:
                from_vessel_seen_ids.add(ts_subOperationId)
                from_vessel_row = {
                    "ts_subOperationId": ts_subOperationId,
                    "ts_name": safe_get(from_vessel.get("name")),
                    "ts_vessel_id": safe_get(from_vessel.get("id")),
                    "ts_volOut": safe_get(from_vessel.get("volOut")),
                    "ts_volOutUnit": safe_get(from_vessel.get("volOutUnit")),
                }
                ts_transactions_from_vessel_table.append(from_vessel_row)
            before_details = safe_get(from_vessel.get("beforeDetails"))
            if before_details:
                if ts_subOperationId not in from_vessel_before_details_seen_ids:
                    from_vessel_before_details_seen_ids.add(ts_subOperationId)
                    before_details_row = {
                        "ts_subOperationId": ts_subOperationId,
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
                    }
                    batch_details = safe_get(before_details.get("batchDetails"))
                    if batch_details:
                        # Deduplicate batchDetails child tables
                        vintage_id = safe_get_path(batch_details, ["vintage", "id"])
                        if vintage_id:
                            ts_batchDetails_vintage_table[vintage_id] = {
                                "vintage_id": vintage_id,
                                "vintage_name": safe_get_path(batch_details, ["vintage", "name"])
                            }
                        variety_id = safe_get_path(batch_details, ["variety", "id"])
                        if variety_id:
                            ts_batchDetails_variety_table[variety_id] = {
                                "variety_id": variety_id,
                                "variety_name": safe_get_path(batch_details, ["variety", "name"])
                            }
                        region_id = safe_get_path(batch_details, ["region", "id"])
                        if region_id:
                            ts_batchDetails_region_table[region_id] = {
                                "region_id": region_id,
                                "region_name": safe_get_path(batch_details, ["region", "name"])
                            }
                        before_details_row.update({
                            "ts_batchDetails_name": safe_get(batch_details.get("name")),
                            "ts_batchDetails_description": safe_get(batch_details.get("description")),
                            "ts_batchDetails_vintage_id": vintage_id,
                            "ts_batchDetails_variety_id": variety_id,
                            "ts_batchDetails_region_id": region_id,
                        })
                    ts_transactions_from_vessel_before_details_table.append(before_details_row)
            after_details = safe_get(from_vessel.get("afterDetails"))
            if after_details:
                if ts_subOperationId not in from_vessel_after_details_seen_ids:
                    from_vessel_after_details_seen_ids.add(ts_subOperationId)
                    after_details_row = {
                        "ts_subOperationId": ts_subOperationId,
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
                    }
                    batch_details = safe_get(after_details.get("batchDetails"))
                    if batch_details:
                        # Deduplicate batchDetails child tables
                        vintage_id = safe_get_path(batch_details, ["vintage", "id"])
                        if vintage_id:
                            ts_batchDetails_vintage_table[vintage_id] = {
                                "vintage_id": vintage_id,
                                "vintage_name": safe_get_path(batch_details, ["vintage", "name"])
                            }
                        variety_id = safe_get_path(batch_details, ["variety", "id"])
                        if variety_id:
                            ts_batchDetails_variety_table[variety_id] = {
                                "variety_id": variety_id,
                                "variety_name": safe_get_path(batch_details, ["variety", "name"])
                            }
                        region_id = safe_get_path(batch_details, ["region", "id"])
                        if region_id:
                            ts_batchDetails_region_table[region_id] = {
                                "region_id": region_id,
                                "region_name": safe_get_path(batch_details, ["region", "name"])
                            }
                        after_details_row.update({
                            "ts_batchDetails_name": safe_get(batch_details.get("name")),
                            "ts_batchDetails_description": safe_get(batch_details.get("description")),
                            "ts_batchDetails_vintage_id": vintage_id,
                            "ts_batchDetails_variety_id": variety_id,
                            "ts_batchDetails_region_id": region_id,
                        })
                    ts_transactions_from_vessel_after_details_table.append(after_details_row)

        if to_vessel:
            if ts_subOperationId not in to_vessel_seen_ids:
                to_vessel_seen_ids.add(ts_subOperationId)
                to_vessel_row = {
                    "ts_subOperationId": ts_subOperationId,
                    "ts_name": safe_get(to_vessel.get("name")),
                    "ts_vessel_id": safe_get(to_vessel.get("id")),
                    "ts_volIn": safe_get(to_vessel.get("volIn")),
                    "ts_volInUnit": safe_get(to_vessel.get("volInUnit")),
                }
                ts_transactions_to_vessel_table.append(to_vessel_row)
            before_details = safe_get(to_vessel.get("beforeDetails"))
            if before_details:
                if ts_subOperationId not in to_vessel_before_details_seen_ids:
                    to_vessel_before_details_seen_ids.add(ts_subOperationId)
                    before_details_row = {
                        "ts_subOperationId": ts_subOperationId,
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
                    }
                    batch_details = safe_get(before_details.get("batchDetails"))
                    if batch_details:
                        # Deduplicate batchDetails child tables
                        vintage_id = safe_get_path(batch_details, ["vintage", "id"])
                        if vintage_id:
                            ts_batchDetails_vintage_table[vintage_id] = {
                                "vintage_id": vintage_id,
                                "vintage_name": safe_get_path(batch_details, ["vintage", "name"])
                            }
                        variety_id = safe_get_path(batch_details, ["variety", "id"])
                        if variety_id:
                            ts_batchDetails_variety_table[variety_id] = {
                                "variety_id": variety_id,
                                "variety_name": safe_get_path(batch_details, ["variety", "name"])
                            }
                        region_id = safe_get_path(batch_details, ["region", "id"])
                        if region_id:
                            ts_batchDetails_region_table[region_id] = {
                                "region_id": region_id,
                                "region_name": safe_get_path(batch_details, ["region", "name"])
                            }
                        before_details_row.update({
                            "ts_batchDetails_name": safe_get(batch_details.get("name")),
                            "ts_batchDetails_description": safe_get(batch_details.get("description")),
                            "ts_batchDetails_vintage_id": vintage_id,
                            "ts_batchDetails_variety_id": variety_id,
                            "ts_batchDetails_region_id": region_id,
                        })
                    ts_transactions_to_vessel_before_details_table.append(before_details_row)
            after_details = safe_get(to_vessel.get("afterDetails"))
            if after_details:
                if ts_subOperationId not in to_vessel_after_details_seen_ids:
                    to_vessel_after_details_seen_ids.add(ts_subOperationId)
                    after_details_row = {
                        "ts_subOperationId": ts_subOperationId,
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
                    }
                    batch_details = safe_get(after_details.get("batchDetails"))
                    if batch_details:
                        # Deduplicate batchDetails child tables
                        vintage_id = safe_get_path(batch_details, ["vintage", "id"])
                        if vintage_id:
                            ts_batchDetails_vintage_table[vintage_id] = {
                                "vintage_id": vintage_id,
                                "vintage_name": safe_get_path(batch_details, ["vintage", "name"])
                            }
                        variety_id = safe_get_path(batch_details, ["variety", "id"])
                        if variety_id:
                            ts_batchDetails_variety_table[variety_id] = {
                                "variety_id": variety_id,
                                "variety_name": safe_get_path(batch_details, ["variety", "name"])
                            }
                        region_id = safe_get_path(batch_details, ["region", "id"])
                        if region_id:
                            ts_batchDetails_region_table[region_id] = {
                                "region_id": region_id,
                                "region_name": safe_get_path(batch_details, ["region", "name"])
                            }
                        after_details_row.update({
                            "ts_batchDetails_name": safe_get(batch_details.get("name")),
                            "ts_batchDetails_description": safe_get(batch_details.get("description")),
                            "ts_batchDetails_vintage_id": vintage_id,
                            "ts_batchDetails_variety_id": variety_id,
                            "ts_batchDetails_region_id": region_id,
                        })
                    ts_transactions_to_vessel_after_details_table.append(after_details_row)

        loss_details = safe_get(transaction.get("lossDetails"))
        if loss_details:
            if ts_subOperationId not in loss_details_seen_ids:
                loss_details_seen_ids.add(ts_subOperationId)
                loss_details_row = {
                    "ts_subOperationId": ts_subOperationId,
                    "ts_volume": safe_get(loss_details.get("volume")),
                    "ts_volumeUnit": safe_get(loss_details.get("volumeUnit")),
                    "ts_reason": safe_get(loss_details.get("reason")),
                }
                ts_transactions_loss_details_table.append(loss_details_row)

        analysis_ops = safe_get(transaction.get("analysisOps"))
        if analysis_ops:
            metrics = safe_get(analysis_ops.get("metrics")) or []
            for metric in metrics:
                key = (ts_subOperationId, safe_get(metric.get("id")))
                if key not in analysis_metrics_seen_keys:
                    analysis_metrics_seen_keys.add(key)
                    row = {
                        "ts_subOperationId": ts_subOperationId,
                        "ts_metric_id": safe_get(metric.get("id")),
                        "ts_vesselId": safe_get(analysis_ops.get("vesselId")),
                        "ts_vesselName": safe_get(analysis_ops.get("vesselName")),
                        "ts_batchId": safe_get(analysis_ops.get("batchId")),
                        "ts_batchName": safe_get(analysis_ops.get("batchName")),
                        "ts_templateId": safe_get(analysis_ops.get("templateId")),
                        "ts_templateName": safe_get(analysis_ops.get("templateName")),
                        "ts_metric_name": safe_get(metric.get("name")),
                        "ts_metric_value": safe_get(metric.get("value")),
                        "ts_metric_txtValue": safe_get(metric.get("txtValue")),
                        "ts_metric_unit": safe_get(metric.get("unit")),
                    }
                    ts_transactions_analysis_metrics_table.append(row)

        additional_details = safe_get(transaction.get("additionalDetails"))
        if additional_details:
            if ts_subOperationId not in additional_details_seen_ids:
                additional_details_seen_ids.add(ts_subOperationId)
                additional_row = {
                    "ts_subOperationId": ts_subOperationId,
                    "ts_summary": flatten_value(safe_get(additional_details.get("summary"))),
                    "ts_bookingNo": flatten_value(safe_get(additional_details.get("bookingNo"))),
                    "ts_owner": flatten_value(safe_get(additional_details.get("owner"))),
                    "ts_netAmountUnit": flatten_value(safe_get(additional_details.get("netAmountUnit"))),
                    "ts_netAmount": flatten_value(safe_get(additional_details.get("netAmount"))),
                    "ts_vintage": flatten_value(safe_get(additional_details.get("vintage"))),
                    "ts_subAva": flatten_value(safe_get(additional_details.get("subAva"))),
                    "ts_block": flatten_value(safe_get(additional_details.get("block"))),
                    "ts_varietal": flatten_value(safe_get(additional_details.get("varietal"))),
                    "ts_grower": flatten_value(safe_get(additional_details.get("grower"))),
                    "ts_harvestMethod": flatten_value(safe_get(additional_details.get("harvestMethod"))),
                    "ts_dispatchNo": flatten_value(safe_get(additional_details.get("dispatchNo"))),
                    "ts_crusher": flatten_value(safe_get(additional_details.get("crusher"))),
                    "ts_dockets": flatten_value(safe_get(additional_details.get("dockets"))),
                    "ts_fractionType": flatten_value(safe_get(additional_details.get("fractionType"))),
                    "ts_press": flatten_value(safe_get(additional_details.get("press"))),
                    "ts_fruitProcess": flatten_value(safe_get(additional_details.get("fruitProcess"))),
                    "ts_crush": flatten_value(safe_get(additional_details.get("fruitProcess")))
                }
                trimmed_row = trim_row(additional_row, MAX_LENGTHS["transactions_additional_details"])
                # Extraction table: operationTypeId==0 ("Extraction")
                if ts_operationTypeId == 0:
                    ts_extraction_table.append(trimmed_row)
                # Grape intake table: operationTypeId==4 ("Intake")
                if ts_operationTypeId == 4:
                    ts_grape_intake_table.append(trimmed_row)
                ts_transactions_additional_details_table.append(trimmed_row)

            extraction = safe_get(additional_details.get("extraction"))
            if extraction:
                parcels = safe_get(extraction.get("parcels")) or []
                for parcel in parcels:
                    ts_docket_val = safe_get(parcel.get("docket"))
                    if ts_docket_val and ts_docket_val not in extraction_parcels_seen_dockets:
                        extraction_parcels_seen_dockets.add(ts_docket_val)
                        parcel_row = {
                            "ts_docket": ts_docket_val,
                            "ts_subOperationId": ts_subOperationId,
                            "ts_bookingNo": safe_get(parcel.get("bookingNo")),
                            "ts_growerId": safe_get(parcel.get("growerId")),
                            "ts_growerName": safe_get(parcel.get("growerName")),
                            "ts_vineyardId": safe_get(parcel.get("vineyardId")),
                            "ts_vineyardName": safe_get(parcel.get("vineyardName")),
                            "ts_blockId": safe_get(parcel.get("blockId")),
                            "ts_blockName": safe_get(parcel.get("blockName")),
                            "ts_weight": safe_get(parcel.get("weight")),
                            "ts_weightUnit": safe_get(parcel.get("weightUnit")),
                        }
                        ts_transactions_extraction_parcels_table.append(parcel_row)

        addition_ops = safe_get(transaction.get("additionOps"))
        if addition_ops:
            if ts_subOperationId not in addition_ops_seen_ids:
                addition_ops_seen_ids.add(ts_subOperationId)
                addition_row = {
                    "ts_subOperationId": ts_subOperationId,
                    "ts_vesselId": safe_get(addition_ops.get("vesselId")),
                    "ts_vesselName": safe_get(addition_ops.get("vesselName")),
                    "ts_batchId": safe_get(addition_ops.get("batchId")),
                    "ts_batchName": safe_get(addition_ops.get("batchName")),
                    "ts_templateId": safe_get(addition_ops.get("templateId")),
                    "ts_templateName": safe_get(addition_ops.get("templateName")),
                    "ts_changeToState": safe_get(addition_ops.get("changeToState")),
                    "ts_volume": safe_get(addition_ops.get("volume")),
                    "ts_amount": safe_get(addition_ops.get("amount")),
                    "ts_unit": safe_get(addition_ops.get("unit")),
                    "ts_lotNumbers": ",".join(safe_get(addition_ops.get("lotNumbers")) or []) if addition_ops.get("lotNumbers") else None
                }
                additive = safe_get(addition_ops.get("additive"))
                if additive:
                    addition_row.update({
                        "ts_additive_id": safe_get(additive.get("id")),
                        "ts_additive_name": safe_get(additive.get("name")),
                        "ts_additive_description": safe_get(additive.get("description")),
                    })
                ts_transactions_addition_ops_table.append(addition_row)
            else:
                print(f"SKIPPING duplicate additionOps for ts_subOperationId={ts_subOperationId} from file {json_file}")

# ...[rest of your file unchanged: writing tables, etc.]...

# Write out the new table for special transfers


# --- Update grape_intake_table with extraction_table fraction fields for matching dockets ---
extraction_docket_map = {}
for row in ts_extraction_table:
    for docket in get_docket_keys(row):
        extraction_docket_map[docket] = row

for intake_row in ts_grape_intake_table:
    for docket in get_docket_keys(intake_row):
        extraction_row = extraction_docket_map.get(docket)
        if extraction_row:
            for field in ["ts_fractionType", "ts_press", "ts_fruitProcess"]:
                val = intake_row.get(field)
                if val in [None, "", "NULL"]:
                    ext_val = extraction_row.get(field)
                    if ext_val not in [None, "", "NULL"]:
                        intake_row[field] = ext_val

# --- Build unique_dockets_table with merged top-level additional_details fields ---
unique_dockets_set = set()
docket_details_map = {}
details_fields = [
    "ts_subOperationId",
    "ts_summary",
    "ts_bookingNo",
    "ts_owner",
    "ts_netAmountUnit",
    "ts_netAmount",
    "ts_vintage",
    "ts_subAva",
    "ts_block",
    "ts_varietal",
    "ts_grower",
    "ts_harvestMethod",
    "ts_dispatchNo",
    "ts_crusher",
    "ts_dockets",
    "ts_fractionType",
    "ts_press",
    "ts_fruitProcess"
]

for row in ts_transactions_additional_details_table:
    for docket in get_docket_keys(row):
        unique_dockets_set.add(docket)
        details = docket_details_map.setdefault(docket, {})
        for field in details_fields:
            val = row.get(field)
            if val not in [None, "", "NULL"]:
                prev_val = details.get(field)
                if prev_val in [None, "", "NULL"]:
                    details[field] = val

unique_dockets_table = [{"ts_docket": d, **docket_details_map[d]} for d in sorted(unique_dockets_set)]

# --- Build extracted_gallons table ---
extracted_gallons_table = []
extracted_gallons_dockets_seen = set()

subOp_lookup = {safe_get(trans.get("subOperationId")): trans for trans in all_transactions_by_subOp.values()}

for row in ts_extraction_table:
    sub_op_id = row.get("ts_subOperationId")
    trans = subOp_lookup.get(sub_op_id)
    to_vessel = safe_get(trans.get("toVessel")) if trans else None
    to_vessel_name = safe_get(to_vessel.get("name")) if to_vessel else None
    to_vessel_volIn = safe_get(to_vessel.get("volIn")) if to_vessel else None
    for docket in get_docket_keys(row):
        if docket and docket not in extracted_gallons_dockets_seen:
            extracted_gallons_dockets_seen.add(docket)
            extracted_gallons_table.append({
                "ts_docket": docket,
                "toVessel_name": to_vessel_name,
                "toVessel_volIn": to_vessel_volIn
            })

# --- Split gallons by tonnage ---
tonnage_lookup = {row["ts_docket"]: float(row.get("ts_netAmount", 0)) for row in unique_dockets_table}

grouped = defaultdict(list)
for rec in extracted_gallons_table:
    key = (rec["toVessel_name"], rec["toVessel_volIn"])
    grouped[key].append(rec["ts_docket"])

split_gallons_table = []
for (vessel, volIn), dockets in grouped.items():
    tonnages = [tonnage_lookup.get(d, 0) for d in dockets]
    total_tonnage = sum(tonnages)
    for docket, tonnage in zip(dockets, tonnages):
        gallons = (tonnage / total_tonnage * volIn) if total_tonnage > 0 else None
        split_gallons_table.append({
            "ts_docket": docket,
            "toVessel_name": vessel,
            "toVessel_volIn": volIn,
            "allocated_gallons": round(gallons, 2) if gallons is not None else None,
            "ts_netAmount": tonnage,
            "tonnage_total_for_vessel": round(total_tonnage, 2)
        })

# --- Master merged output ---
unique_dockets_lookup = {row["ts_docket"]: row for row in unique_dockets_table}
master_table = []

for split_row in split_gallons_table:
    docket = split_row["ts_docket"]
    unique_row = unique_dockets_lookup.get(docket, {})
    # Find the subOperationId for this docket
    sub_op_id = unique_row.get("ts_subOperationId") or None
    transaction = all_transactions_by_subOp.get(sub_op_id)
    # Add transaction-level fields
    transaction_fields = {}
    if transaction:
        transaction_fields = {
            "ts_formattedDate": safe_get(transaction.get("formattedDate")),
            "ts_workorder": safe_get(transaction.get("workorder")),
            "ts_jobNumber": safe_get(transaction.get("jobNumber")),
            "ts_treatment": safe_get(transaction.get("treatment")),
            "ts_completedBy": safe_get(transaction.get("completedBy")),
            "ts_winery": safe_get(transaction.get("winery")),
        }
        to_vessel = safe_get(transaction.get("toVessel"))
        after_details = safe_get(to_vessel.get("afterDetails")) if to_vessel else None
        if after_details:
            transaction_fields["ts_afterDetails_batch"] = safe_get(after_details.get("batch"))
            # To add more fields, just replicate this line for each field you want.
            # Example: transaction_fields["ts_afterDetails_volume"] = safe_get(after_details.get("volume"))
    merged_row = {**unique_row, **split_row, **transaction_fields}
    master_table.append(merged_row)

# --- Build unique_dispatchNos_table with merged fields ---
unique_dispatchNos_set = set()
dispatchNo_details_map = {}

dispatch_fields = [
    "ts_subOperationId",
    "ts_dispatchNo",
    "ts_summary",
    "ts_bookingNo",
    "ts_owner",
    "ts_netAmountUnit",
    "ts_netAmount",
    "ts_vintage",
    "ts_subAva",
    "ts_block",
    "ts_varietal",
    "ts_grower",
    "ts_harvestMethod",
    "ts_crusher",
    "ts_dockets",
    "ts_fractionType",
    "ts_press",
    "ts_fruitProcess"
]

for row in ts_transactions_additional_details_table:
    # Handle dispatchNo as string or comma-separated list
    dispatchNos = row.get("ts_dispatchNo")
    if dispatchNos is None:
        continue
    if isinstance(dispatchNos, list):
        dispatch_list = [str(d).strip() for d in dispatchNos if str(d).strip()]
    else:
        dispatch_list = [d.strip() for d in str(dispatchNos).split(",") if d.strip()]
    for dispatchNo in dispatch_list:
        unique_dispatchNos_set.add(dispatchNo)
        details = dispatchNo_details_map.setdefault(dispatchNo, {})
        for field in dispatch_fields:
            val = row.get(field)
            if val not in [None, "", "NULL"]:
                prev_val = details.get(field)
                if prev_val in [None, "", "NULL"]:
                    details[field] = val

# Collect transaction-level metadata for each dispatchNo

unique_dispatchNos_table = []
for dispatchNo in sorted(unique_dispatchNos_set):
    details = dispatchNo_details_map.get(dispatchNo, {})
    sub_op_id = details.get("ts_subOperationId")
    transaction = all_transactions_by_subOp.get(sub_op_id)
    transaction_fields = {}
    if transaction:
        transaction_fields = {
            "ts_formattedDate": safe_get(transaction.get("formattedDate")),
            "ts_workorder": safe_get(transaction.get("workorder")),
            "ts_jobNumber": safe_get(transaction.get("jobNumber")),
            "ts_treatment": safe_get(transaction.get("treatment")),
            "ts_completedBy": safe_get(transaction.get("completedBy")),
            "ts_winery": safe_get(transaction.get("winery")),
            "volOut": safe_get(transaction.get("fromVessel", {}).get("volOut")),
        }
    merged_row = {"ts_dispatchNo": dispatchNo, **details, **transaction_fields}
    unique_dispatchNos_table.append(merged_row)

# --- Write to JSON files ---

with open(os.path.join(OUT_DIR, "ts_transfer_operations_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(ts_transfer_operations_table, f)

with open(os.path.join(OUT_DIR, "special_transfer_link_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(special_transfer_link_table, f)
    
with open(os.path.join(OUT_DIR, "special_transfer_intransit_to_intransit_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(special_transfer_intransit_to_intransit_table, f)

with open(os.path.join(OUT_DIR, "special_transfer_from_intransit_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(special_transfer_from_intransit_table, f)

with open(os.path.join(OUT_DIR, "special_transfer_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(special_transfer_table, f)

with open(os.path.join(OUT_DIR, "split_gallons_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(split_gallons_table, f)

with open(os.path.join(OUT_DIR, "ts_transactions.json"), "w", encoding="utf-8") as f:
    safe_json_dump(ts_transactions_table, f)
with open(os.path.join(OUT_DIR, "ts_transactions_from_vessel_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(ts_transactions_from_vessel_table, f)
with open(os.path.join(OUT_DIR, "ts_transactions_from_vessel_before_details_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(ts_transactions_from_vessel_before_details_table, f)
with open(os.path.join(OUT_DIR, "ts_transactions_from_vessel_after_details_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(ts_transactions_from_vessel_after_details_table, f)
with open(os.path.join(OUT_DIR, "ts_transactions_to_vessel_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(ts_transactions_to_vessel_table, f)
with open(os.path.join(OUT_DIR, "ts_transactions_to_vessel_before_details_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(ts_transactions_to_vessel_before_details_table, f)
with open(os.path.join(OUT_DIR, "ts_transactions_to_vessel_after_details_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(ts_transactions_to_vessel_after_details_table, f)
# Write new transfer operations table!
with open(os.path.join(OUT_DIR, "ts_transfer_operations_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(ts_transfer_operations_table, f)
# Write child tables for linking
with open(os.path.join(ID_OUT_DIR, "ts_batchDetails_vintage_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(list(ts_batchDetails_vintage_table.values()), f)
with open(os.path.join(ID_OUT_DIR, "ts_batchDetails_variety_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(list(ts_batchDetails_variety_table.values()), f)
with open(os.path.join(ID_OUT_DIR, "ts_batchDetails_region_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(list(ts_batchDetails_region_table.values()), f)

print("Split complete! JSON tables written to", OUT_DIR, "and", ID_OUT_DIR)