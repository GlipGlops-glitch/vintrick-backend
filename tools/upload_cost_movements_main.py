# python tools/upload_cost_movements_main.py

import json
import os
import math
import datetime
import pandas as pd
from collections import defaultdict
from utils.helpers import safe_get, safe_get_path, convert_epoch_columns

# Input/Output locations
JSON_DIR = os.getenv("COST_MOVEMENTS_JSON", "Main/data/GET--business_unit_transactions_by_day")
OUT_DIR = os.getenv("COST_MOVEMENTS_SPLIT_DIR", "Main/data/GET--business_unit_transactions_by_day/tables")
ID_OUT_DIR = "Main/data/id_tables"

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ID_OUT_DIR, exist_ok=True)

# Discover files
json_files = [
    os.path.join(JSON_DIR, fname)
    for fname in os.listdir(JSON_DIR)
    if fname.endswith(".json") and os.path.isfile(os.path.join(JSON_DIR, fname))
]

print(f"Found {len(json_files)} files to process in {JSON_DIR} (not going into {OUT_DIR}).")

def _sanitize_value(v):
    # Datetimes -> ISO string
    if isinstance(v, (pd.Timestamp, datetime.datetime, datetime.date)):
        # Standardize format for readability
        if isinstance(v, (pd.Timestamp, datetime.datetime)):
            return v.strftime("%Y-%m-%d %H:%M:%S")
        return v.isoformat()

    # Numpy scalars -> Python scalars
    if hasattr(v, "item"):
        try:
            v = v.item()
        except Exception:
            pass

    # NaN/None handling
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass

    # Replace non-finite numbers with null
    if isinstance(v, float) and not math.isfinite(v):
        return None

    # Normalize integer-looking floats to int (e.g., 3.0 -> 3)
    if isinstance(v, float) and math.isfinite(v) and v.is_integer():
        return int(v)

    return v

def _sanitize_records(records):
    out = []
    for row in records:
        out.append({k: _sanitize_value(v) for k, v in row.items()})
    return out

def safe_json_dump(data, file):
    # Uniformly produce a list[dict] and sanitize it
    if isinstance(data, pd.DataFrame):
        records = data.to_dict(orient="records")
        records = _sanitize_records(records)
        json.dump(records, file, indent=2, ensure_ascii=False, allow_nan=False)
    elif isinstance(data, list):
        records = _sanitize_records(data)
        json.dump(records, file, indent=2, ensure_ascii=False, allow_nan=False)
    else:
        # Single dict or other types
        json.dump(_sanitize_value(data), file, indent=2, ensure_ascii=False, allow_nan=False)

# Master activity table (one row per activity)
cm_activities = []

# Simple 1:1 per activity tables
cm_volume_delta = []
cm_cost_delta = []
cm_references = []

# 1:N tables
cm_impacted_allocations = []

# ID/lookup tables (dedup by id)
cm_cost_owners = {}       # {id: {id, name, extId}}
cm_wineries = {}          # {id: {id, name, businessUnit}}
cm_programs = {}          # {id: {id, name, code}}
cm_customers = {}         # {id: {id, name, extId}}
cm_vendors = {}           # {id: {id, name, extId}}

# Seen sets for 1:1 per-activity tables
seen_volume_delta = set()
seen_cost_delta = set()
seen_references = set()

# Helper to register ID tables
def register_cost_owner(node):
    if not node:
        return None
    oid = safe_get(node.get("id"))
    if oid is None:
        return None
    if oid not in cm_cost_owners:
        cm_cost_owners[oid] = {
            "id": oid,
            "name": safe_get(node.get("name")),
            "extId": safe_get(node.get("extId")),
        }
    return oid

def register_winery(node):
    if not node:
        return None
    wid = safe_get(node.get("id"))
    if wid is None:
        return None
    if wid not in cm_wineries:
        cm_wineries[wid] = {
            "id": wid,
            "name": safe_get(node.get("name")),
            "businessUnit": safe_get(node.get("businessUnit")),
        }
    return wid

def register_program(node):
    if not node:
        return None
    pid = safe_get(node.get("id"))
    if pid is None:
        return None
    if pid not in cm_programs:
        cm_programs[pid] = {
            "id": pid,
            "name": safe_get(node.get("name")),
            "code": safe_get(node.get("code")),
        }
    return pid

def register_customer(node):
    if not node:
        return None
    cid = safe_get(node.get("id"))
    if cid is None:
        return None
    if cid not in cm_customers:
        cm_customers[cid] = {
            "id": cid,
            "name": safe_get(node.get("name")),
            "extId": safe_get(node.get("extId")),
        }
    return cid

def register_vendor(node):
    if not node:
        return None
    vid = safe_get(node.get("id"))
    if vid is None:
        return None
    if vid not in cm_vendors:
        cm_vendors[vid] = {
            "id": vid,
            "name": safe_get(node.get("name")),
            "extId": safe_get(node.get("extId")),
        }
    return vid

def get_activities_from_payload(data, json_file):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ["activities", "businessUnitTransactions", "items", "data", "records"]:
            lst = data.get(key)
            if isinstance(lst, list):
                return lst
        if "activityId" in data or "postedId" in data:
            return [data]
    print(f"WARNING: {json_file} is not a recognized cost movement structure, skipping.")
    return []

# Read and split
for json_file in json_files:
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"ERROR: Could not read {json_file}: {e}")
        continue

    activities = get_activities_from_payload(data, json_file)
    if not activities:
        continue

    for act in activities:
        if not isinstance(act, dict):
            continue

        posted_id = safe_get(act.get("postedId"))
        activity_id = safe_get(act.get("activityId"))

        # Register ID lookups first
        primary_owner_id = register_cost_owner(safe_get(act.get("primaryCostOwner")))
        secondary_owner_id = register_cost_owner(safe_get(act.get("secondaryCostOwner")))
        primary_winery_id = register_winery(safe_get(act.get("primaryWinery")))
        secondary_winery_id = register_winery(safe_get(act.get("secondaryWinery")))
        program_id = register_program(safe_get(act.get("program")))
        customer_id = register_customer(safe_get(act.get("customer")))
        vendor_id = register_vendor(safe_get(act.get("vendor")))

        # Main activity row
        cm_activities.append({
            "cm_postedId": posted_id,
            "cm_activityId": activity_id,
            "cm_resultOfCorrection": safe_get(act.get("resultOfCorrection")),
            "cm_activityType": safe_get(act.get("activityType")),
            "cm_activitySummary": safe_get(act.get("activitySummary")),
            "cm_activityDate": safe_get(act.get("activityDate")),   # epoch ms; will be converted in-place
            "cm_postedDate": safe_get(act.get("postedDate")),       # epoch ms; will be converted in-place
            "cm_primaryCostTarget": safe_get(act.get("primaryCostTarget")),
            "cm_secondaryCostTarget": safe_get(act.get("secondaryCostTarget")),
            "cm_location": safe_get(act.get("location")),
            "cm_vessel": safe_get(act.get("vessel")),
            "cm_wineBatch": safe_get(act.get("wineBatch")),
            # FKs
            "cm_primaryCostOwner_id": primary_owner_id,
            "cm_secondaryCostOwner_id": secondary_owner_id,
            "cm_primaryWinery_id": primary_winery_id,
            "cm_secondaryWinery_id": secondary_winery_id,
            "cm_program_id": program_id,
            "cm_customer_id": customer_id,
            "cm_vendor_id": vendor_id,
            # Convenience: copy references to main as well
            "cm_bulkSalesOrder": safe_get_path(act, ["references", "bulkSalesOrder"]),
            "cm_bulkPurchaseOrder": safe_get_path(act, ["references", "bulkPurchaseOrder"]),
            "cm_externalWorkOrder": safe_get_path(act, ["references", "externalWorkOrder"]),
            "cm_workOrder": safe_get_path(act, ["references", "workOrder"]),
            "cm_jobNumber": safe_get_path(act, ["references", "jobNumber"]),
            "cm_billOfLadingNumber": safe_get_path(act, ["references", "billOfLadingNumber"]),
        })

        # Volume delta (1:1)
        if posted_id is not None and posted_id not in seen_volume_delta:
            seen_volume_delta.add(posted_id)
            vol = safe_get(act.get("volumeDelta")) or {}
            cm_volume_delta.append({
                "cm_postedId": posted_id,
                "unit": safe_get(vol.get("unit")),
                "value": safe_get(vol.get("value")),
            })

        # Cost delta (1:1)
        if posted_id is not None and posted_id not in seen_cost_delta:
            seen_cost_delta.add(posted_id)
            cst = safe_get(act.get("costDelta")) or {}
            cm_cost_delta.append({
                "cm_postedId": posted_id,
                "total": safe_get(cst.get("total")),
                "fruit": safe_get(cst.get("fruit")),
                "overhead": safe_get(cst.get("overhead")),
                "storage": safe_get(cst.get("storage")),
                "additive": safe_get(cst.get("additive")),
                "bulk": safe_get(cst.get("bulk")),
                "packaging": safe_get(cst.get("packaging")),
                "operation": safe_get(cst.get("operation")),
                "freight": safe_get(cst.get("freight")),
                "other": safe_get(cst.get("other")),
            })

        # References (1:1)
        if posted_id is not None and posted_id not in seen_references:
            seen_references.add(posted_id)
            refs = safe_get(act.get("references")) or {}
            cm_references.append({
                "cm_postedId": posted_id,
                "bulkSalesOrder": safe_get(refs.get("bulkSalesOrder")),
                "bulkPurchaseOrder": safe_get(refs.get("bulkPurchaseOrder")),
                "externalWorkOrder": safe_get(refs.get("externalWorkOrder")),
                "workOrder": safe_get(refs.get("workOrder")),
                "jobNumber": safe_get(refs.get("jobNumber")),
                "billOfLadingNumber": safe_get(refs.get("billOfLadingNumber")),
            })

        # Impacted allocations (1:N)
        impacted = safe_get(act.get("impactedAllocations")) or []
        for item in impacted:
            if not isinstance(item, dict):
                continue
            cm_impacted_allocations.append({
                "cm_postedId": posted_id,
                "productName": safe_get(item.get("productName")),
                "vintage": safe_get(item.get("vintage")),
                "itemCode": safe_get(item.get("itemCode")),
                "name": safe_get(item.get("name")),
            })

# Convert epochs in-place for the activity DataFrame
activities_df = pd.DataFrame(cm_activities)
if not activities_df.empty:
    # Mirror into '*Time' so the helper converts them, then write back
    tmp_cols = []
    if "cm_activityDate" in activities_df.columns:
        activities_df["cm_activityTime"] = activities_df["cm_activityDate"]
        tmp_cols.append(("cm_activityTime", "cm_activityDate"))
    if "cm_postedDate" in activities_df.columns:
        activities_df["cm_postedTime"] = activities_df["cm_postedDate"]
        tmp_cols.append(("cm_postedTime", "cm_postedDate"))

    activities_df = convert_epoch_columns(activities_df)

    # Copy converted datetimes back into original columns, drop temps
    for tmp_col, orig_col in tmp_cols:
        if tmp_col in activities_df.columns:
            activities_df[orig_col] = activities_df[tmp_col]
            activities_df.drop(columns=[tmp_col], inplace=True, errors="ignore")

# Write main and split tables (safe_json_dump ensures valid JSON: no NaN/Infinity)
with open(os.path.join(OUT_DIR, "cm_activities.json"), "w", encoding="utf-8") as f:
    safe_json_dump(activities_df if not activities_df.empty else cm_activities, f)

with open(os.path.join(OUT_DIR, "cm_volume_delta.json"), "w", encoding="utf-8") as f:
    safe_json_dump(cm_volume_delta, f)

with open(os.path.join(OUT_DIR, "cm_cost_delta.json"), "w", encoding="utf-8") as f:
    safe_json_dump(cm_cost_delta, f)

with open(os.path.join(OUT_DIR, "cm_references.json"), "w", encoding="utf-8") as f:
    safe_json_dump(cm_references, f)

with open(os.path.join(OUT_DIR, "cm_impacted_allocations.json"), "w", encoding="utf-8") as f:
    safe_json_dump(cm_impacted_allocations, f)

# Write ID/lookup tables
with open(os.path.join(ID_OUT_DIR, "cm_cost_owners.json"), "w", encoding="utf-8") as f:
    safe_json_dump(list(cm_cost_owners.values()), f)

with open(os.path.join(ID_OUT_DIR, "cm_wineries.json"), "w", encoding="utf-8") as f:
    safe_json_dump(list(cm_wineries.values()), f)

with open(os.path.join(ID_OUT_DIR, "cm_programs.json"), "w", encoding="utf-8") as f:
    safe_json_dump(list(cm_programs.values()), f)

with open(os.path.join(ID_OUT_DIR, "cm_customers.json"), "w", encoding="utf-8") as f:
    safe_json_dump(list(cm_customers.values()), f)

with open(os.path.join(ID_OUT_DIR, "cm_vendors.json"), "w", encoding="utf-8") as f:
    safe_json_dump(list(cm_vendors.values()), f)

print("Cost movement split complete! JSON tables written to", OUT_DIR, "and", ID_OUT_DIR)