# python tools/upload_transactions_main_v2_sandbox.py

#!/usr/bin/env python3
"""
Refactored transactions uploader/splitter.

Key improvements:
- Robust parsing and error handling (malformed JSON, missing Tanks file)
- Argparse + logging (configurable paths, in-transit building name, volume tolerance)
- Deduplicated repeated code (vessel details and batchDetails extraction)
- Correct sub-operation lookup (only real transactions)
- Build special transfer links after full scan with numeric tolerance
- Safer truthy check for "reversed"
- Safer numeric handling for netAmount and volume fields
- Safer list flattening that avoids "None" strings
- Single write for each output file
"""
import argparse
import json
import logging
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
from utils.helpers import safe_get_path, safe_get


# --------------------------- Defaults (overridable via CLI) ---------------------------

DEFAULT_JSON_DIR = os.getenv("TRANSACTIONS_JSON", "Main/data/GET--transactions_by_day_sandbox")
DEFAULT_OUT_DIR = os.getenv("TRANSACTIONS_SPLIT_DIR", "Main/data/GET--transactions_by_day_sandbox/tables")
DEFAULT_ID_OUT_DIR = "Main/data/id_tables_sandbox"
DEFAULT_TANKS_FILE = os.path.join(DEFAULT_ID_OUT_DIR, "Tanks_All_sandbox.json")
DEFAULT_INTRANSIT_BUILDING_NAME = "In-Transit-Bldg"
DEFAULT_VOL_TOLERANCE = 0.5  # tolerance for linking transfers on volume

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
        "ts_press": 50,
    }
}


# --------------------------- CLI & Logging ---------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Process and split transactions JSON files into tables.")
    p.add_argument("--json-dir", default=DEFAULT_JSON_DIR, help="Directory with source transactions .json files.")
    p.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Directory to write split tables.")
    p.add_argument("--id-out-dir", default=DEFAULT_ID_OUT_DIR, help="Directory to write ID tables.")
    p.add_argument("--tanks-file", default=DEFAULT_TANKS_FILE, help="Path to Tanks_All.json for building lookup.")
    p.add_argument("--intransit-name", default=DEFAULT_INTRANSIT_BUILDING_NAME, help="Winery Building name for in-transit.")
    p.add_argument("--vol-tolerance", type=float, default=DEFAULT_VOL_TOLERANCE, help="Volume tolerance for linking transfers.")
    p.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Logging level.")
    return p.parse_args()


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s %(levelname)s %(message)s",
    )


# --------------------------- Helpers ---------------------------

def safe_json_dump(data: Any, file) -> None:
    """Dump lists or DataFrames to JSON with None instead of NaN."""
    if isinstance(data, pd.DataFrame):
        data = data.where(pd.notnull(data), None).to_dict(orient="records")
    elif isinstance(data, list):
        norm = []
        for row in data:
            if isinstance(row, dict):
                row = {k: (None if (isinstance(v, float) and pd.isnull(v)) else v) for k, v in row.items()}
            norm.append(row)
        data = norm
    json.dump(data, file, indent=2, ensure_ascii=False)


def get_docket_keys(row: Dict[str, Any], key: str = "ts_dockets") -> List[str]:
    dockets_val = row.get(key, "")
    if isinstance(dockets_val, list):
        return [str(d).strip() for d in dockets_val if str(d).strip()]
    return [d.strip() for d in str(dockets_val).split(",") if d.strip()]


def flatten_value(val: Any) -> Optional[str]:
    """Flatten lists to comma-separated strings and normalize null-ish values to None."""
    if isinstance(val, list):
        parts = [str(v).strip() for v in val if v not in (None, "", "NULL")]
        return ",".join(parts) if parts else None
    if val in (None, "", "NULL"):
        return None
    # Keep as-is for non-list, non-null-ish (strings or numbers)
    return str(val) if not isinstance(val, (int, float)) else val  # don't convert numbers to string


def to_float_or_none(x: Any) -> Optional[float]:
    try:
        if x in (None, "", "NULL"):
            return None
        return float(x)
    except (TypeError, ValueError):
        return None


def to_int_or_none(x: Any) -> Optional[int]:
    try:
        if x in (None, "", "NULL"):
            return None
        return int(x)
    except (TypeError, ValueError):
        return None


def flatten_numeric_list(val: Any) -> Optional[float]:
    """If list -> sum numeric entries; else try to parse single numeric; else None."""
    if isinstance(val, list):
        nums = [to_float_or_none(v) for v in val]
        nums = [v for v in nums if v is not None]
        return sum(nums) if nums else None
    return to_float_or_none(val)


def trim_row(row: Dict[str, Any], max_lengths: Dict[str, int]) -> Dict[str, Any]:
    for key, maxlen in max_lengths.items():
        val = row.get(key)
        if isinstance(val, str) and maxlen is not None:
            row[key] = val[:maxlen]
    return row


def is_truthy_true(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v == 1
    if isinstance(v, str):
        return v.strip().lower() in {"true", "1", "yes", "y"}
    return False


def load_tanks_lookup(tanks_file: str) -> Dict[str, str]:
    """Return mapping of vessel name -> Winery Building; empty if file missing/unreadable."""
    try:
        with open(tanks_file, "r", encoding="utf-8") as f:
            tanks_all = json.load(f)
        lookup = {}
        for tank in tanks_all:
            vessel = safe_get(tank.get("vessel"))
            bldg = safe_get(tank.get("Winery Building"))
            if vessel is not None:
                lookup[vessel] = bldg
        logging.info("Loaded %d tank records from %s", len(lookup), tanks_file)
        return lookup
    except FileNotFoundError:
        logging.warning("Tanks file not found at %s; in-transit lookups disabled.", tanks_file)
        return {}
    except Exception as e:
        logging.warning("Failed to load tanks file %s: %s; in-transit lookups disabled.", tanks_file, e)
        return {}


# ----- BatchDetails extraction and de-dup tables -----

def update_batch_details_tables(
    batch_details: Dict[str, Any],
    ts_batchDetails_vintage_table: Dict[Any, Dict[str, Any]],
    ts_batchDetails_variety_table: Dict[Any, Dict[str, Any]],
    ts_batchDetails_region_table: Dict[Any, Dict[str, Any]],
) -> Dict[str, Any]:
    """Update 3 ID tables and return fields to attach to row."""
    out = {}
    if not batch_details:
        return out

    vintage_id = safe_get_path(batch_details, ["vintage", "id"])
    if vintage_id:
        ts_batchDetails_vintage_table[vintage_id] = {
            "vintage_id": vintage_id,
            "vintage_name": safe_get_path(batch_details, ["vintage", "name"]),
        }
    variety_id = safe_get_path(batch_details, ["variety", "id"])
    if variety_id:
        ts_batchDetails_variety_table[variety_id] = {
            "variety_id": variety_id,
            "variety_name": safe_get_path(batch_details, ["variety", "name"]),
        }
    region_id = safe_get_path(batch_details, ["region", "id"])
    if region_id:
        ts_batchDetails_region_table[region_id] = {
            "region_id": region_id,
            "region_name": safe_get_path(batch_details, ["region", "name"]),
        }

    out.update({
        "ts_batchDetails_name": safe_get(batch_details.get("name")),
        "ts_batchDetails_description": safe_get(batch_details.get("description")),
        "ts_batchDetails_vintage_id": vintage_id,
        "ts_batchDetails_variety_id": variety_id,
        "ts_batchDetails_region_id": region_id,
    })
    return out


def build_details_row(details: Dict[str, Any]) -> Dict[str, Any]:
    """Common fields for before/after details rows."""
    return {
        "ts_contentsId": safe_get(details.get("contentsId")),
        "ts_batch": safe_get(details.get("batch")),
        "ts_batchId": safe_get(details.get("batchId")),
        "ts_volume": safe_get(details.get("volume")),
        "ts_volumeUnit": safe_get(details.get("volumeUnit")),
        "ts_dip": safe_get(details.get("dip")),
        "ts_state": safe_get(details.get("state")),
        "ts_rawTaxClass": safe_get(details.get("rawTaxClass")),
        "ts_federalTaxClass": safe_get(details.get("federalTaxClass")),
        "ts_stateTaxClass": safe_get(details.get("stateTaxClass")),
        "ts_program": safe_get(details.get("program")),
        "ts_grading": safe_get(details.get("grading")),
        "ts_productCategory": safe_get(details.get("productCategory")),
        "ts_batchOwner": safe_get(details.get("batchOwner")),
        "ts_serviceOrder": safe_get(details.get("serviceOrder")),
        "ts_alcoholicFermentState": safe_get(details.get("alcoholicFermentState")),
        "ts_malolacticFermentState": safe_get(details.get("malolacticFermentState")),
        "ts_revisionName": safe_get(details.get("revisionName")),
        "ts_physicalStateText": safe_get(details.get("physicalStateText")),
    }


def process_vessel_basic(
    side: str,
    vessel: Dict[str, Any],
    sub_op_id: Any,
    seen_ids: Set[Any],
    target_list: List[Dict[str, Any]],
) -> None:
    """Append basic vessel row for 'from' or 'to' if not yet seen for sub_op_id."""
    if sub_op_id in seen_ids:
        return
    seen_ids.add(sub_op_id)

    row = {
        "ts_subOperationId": sub_op_id,
        "ts_name": safe_get(vessel.get("name")),
        "ts_vessel_id": safe_get(vessel.get("id")),
    }
    if side == "from":
        row.update({
            "ts_volOut": safe_get(vessel.get("volOut")),
            "ts_volOutUnit": safe_get(vessel.get("volOutUnit")),
        })
    else:
        row.update({
            "ts_volIn": safe_get(vessel.get("volIn")),
            "ts_volInUnit": safe_get(vessel.get("volInUnit")),
        })
    target_list.append(row)


def process_vessel_details(
    details: Optional[Dict[str, Any]],
    sub_op_id: Any,
    seen_ids: Set[Any],
    target_list: List[Dict[str, Any]],
    ts_batchDetails_vintage_table: Dict[Any, Dict[str, Any]],
    ts_batchDetails_variety_table: Dict[Any, Dict[str, Any]],
    ts_batchDetails_region_table: Dict[Any, Dict[str, Any]],
) -> None:
    """Append details row (before/after) if present and not yet seen for sub_op_id."""
    if not details or sub_op_id in seen_ids:
        return
    seen_ids.add(sub_op_id)

    row = {"ts_subOperationId": sub_op_id, **build_details_row(details)}
    row.update(update_batch_details_tables(
        safe_get(details.get("batchDetails")) or {},
        ts_batchDetails_vintage_table,
        ts_batchDetails_variety_table,
        ts_batchDetails_region_table,
    ))
    target_list.append(row)


def _round_or_none(x: Any, ndigits: int = 3) -> Optional[float]:
    v = to_float_or_none(x)
    return round(v, ndigits) if v is not None else None


def build_special_transfer_links(
    to_list: List[Dict[str, Any]],
    from_list: List[Dict[str, Any]],
    vol_tol: float,
) -> List[Dict[str, Any]]:
    """
    Link 'to in-transit' records to 'from in-transit to non-intransit' records by matching vessel name and approximately matching volume.
    """
    # Index "from" by name and rounded vol bucket
    index: Dict[str, Dict[Optional[float], List[Tuple[int, Dict[str, Any]]]]] = {}
    for idx, row in enumerate(from_list):
        name = row.get("from_ts_name")
        vol = _round_or_none(row.get("from_ts_volOut"))
        index.setdefault(name, {}).setdefault(vol, []).append((idx, row))

    links: List[Dict[str, Any]] = []
    for idx_to, to_row in enumerate(to_list):
        name = to_row.get("to_ts_name")
        vol_in = _round_or_none(to_row.get("to_ts_volIn"))
        buckets = index.get(name, {})
        if vol_in is None or not buckets:
            continue
        for vol_key, candidates in buckets.items():
            if vol_key is None or abs(vol_key - vol_in) > vol_tol:
                continue
            for idx_from, from_row in candidates:
                links.append({
                    "special_transfer_table_idx": idx_to,
                    "special_transfer_table_subOperationId": to_row.get("ts_subOperationId"),
                    "special_transfer_from_intransit_table_idx": idx_from,
                    "special_transfer_from_intransit_table_subOperationId": from_row.get("ts_subOperationId"),
                    "vessel_name": name,
                    "volume_to": to_row.get("to_ts_volIn"),
                    "volume_from": from_row.get("from_ts_volOut"),
                })
    # De-duplicate by subOpId pairs
    seen_pairs: Set[Tuple[Any, Any]] = set()
    deduped: List[Dict[str, Any]] = []
    for l in links:
        key = (l["special_transfer_table_subOperationId"], l["special_transfer_from_intransit_table_subOperationId"])
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        deduped.append(l)
    return deduped


# --------------------------- Main processing ---------------------------

def main() -> None:
    args = parse_args()
    setup_logging(args.log_level)

    json_dir = args.json_dir
    out_dir = args.out_dir
    id_out_dir = args.id_out_dir
    tanks_file = args.tanks_file
    intransit_name = args.intransit_name
    vol_tolerance = args.vol_tolerance

    if not os.path.isdir(json_dir):
        logging.error("JSON dir does not exist: %s", json_dir)
        return

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(id_out_dir, exist_ok=True)

    json_files = [
        os.path.join(json_dir, fname)
        for fname in os.listdir(json_dir)
        if fname.endswith(".json") and os.path.isfile(os.path.join(json_dir, fname))
    ]
    logging.info("Found %d files to process in %s (outputs -> %s).", len(json_files), json_dir, out_dir)

    # Tanks lookup
    tanks_lookup = load_tanks_lookup(tanks_file)

    # Tables with ts_ prefix
    ts_transactions_table: List[Dict[str, Any]] = []
    ts_transactions_from_vessel_table: List[Dict[str, Any]] = []
    ts_transactions_from_vessel_before_details_table: List[Dict[str, Any]] = []
    ts_transactions_from_vessel_after_details_table: List[Dict[str, Any]] = []
    ts_transactions_to_vessel_table: List[Dict[str, Any]] = []
    ts_transactions_to_vessel_before_details_table: List[Dict[str, Any]] = []
    ts_transactions_to_vessel_after_details_table: List[Dict[str, Any]] = []
    ts_transactions_loss_details_table: List[Dict[str, Any]] = []
    ts_transactions_analysis_metrics_table: List[Dict[str, Any]] = []
    ts_transactions_additional_details_table: List[Dict[str, Any]] = []
    ts_transactions_extraction_parcels_table: List[Dict[str, Any]] = []
    ts_transactions_addition_ops_table: List[Dict[str, Any]] = []
    ts_extraction_table: List[Dict[str, Any]] = []
    ts_grape_intake_table: List[Dict[str, Any]] = []
    ts_transfer_operations_table: List[Dict[str, Any]] = []

    # Lookup tables for child entities
    ts_batchDetails_vintage_table: Dict[Any, Dict[str, Any]] = {}
    ts_batchDetails_variety_table: Dict[Any, Dict[str, Any]] = {}
    ts_batchDetails_region_table: Dict[Any, Dict[str, Any]] = {}

    # Dedup sets
    from_vessel_seen_ids: Set[Any] = set()
    from_vessel_before_details_seen_ids: Set[Any] = set()
    from_vessel_after_details_seen_ids: Set[Any] = set()
    to_vessel_seen_ids: Set[Any] = set()
    to_vessel_before_details_seen_ids: Set[Any] = set()
    to_vessel_after_details_seen_ids: Set[Any] = set()
    loss_details_seen_ids: Set[Any] = set()
    additional_details_seen_ids: Set[Any] = set()
    addition_ops_seen_ids: Set[Any] = set()
    analysis_metrics_seen_keys: Set[Tuple[Any, Any]] = set()
    extraction_parcels_seen_dockets: Set[Any] = set()

    # Special transfer tables
    special_transfer_table: List[Dict[str, Any]] = []
    special_transfer_from_intransit_table: List[Dict[str, Any]] = []
    special_transfer_intransit_to_intransit_table: List[Dict[str, Any]] = []

    # subOperationId -> transaction (ONLY real transactions)
    transactions_by_subOp: Dict[Any, Dict[str, Any]] = {}

    # Scan files
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logging.warning("Skipping file %s due to read/parse error: %s", json_file, e)
            continue

        if isinstance(data, dict) and "transactionSummaries" in data:
            transactions = data["transactionSummaries"]
        elif isinstance(data, list):
            transactions = data
        else:
            logging.warning("Skipping file %s; not a valid transactions file.", json_file)
            continue

        if not isinstance(transactions, list):
            logging.warning("Skipping file %s; 'transactions' is not a list.", json_file)
            continue

        for transaction in transactions:
            if not isinstance(transaction, dict):
                logging.debug("Skipping non-dict transaction in %s: %r", json_file, transaction)
                continue

            ts_subOperationId = safe_get(transaction.get("subOperationId"))
            if ts_subOperationId is not None:
                transactions_by_subOp[ts_subOperationId] = transaction

            # Skip reversed
            if is_truthy_true(transaction.get("reversed")):
                continue

            ts_operationTypeId = to_int_or_none(safe_get(transaction.get("operationTypeId")))
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
                "ts_reversed": safe_get(transaction.get("reversed")),
                "ts_workorder": safe_get(transaction.get("workorder")),
                "ts_jobNumber": safe_get(transaction.get("jobNumber")),
                "ts_treatment": safe_get(transaction.get("treatment")),
                "ts_assignedBy": safe_get(transaction.get("assignedBy")),
                "ts_completedBy": safe_get(transaction.get("completedBy")),
                "ts_winery": safe_get(transaction.get("winery")),
            }
            ts_transactions_table.append(transaction_row)

            # Transfer operations table (op type 31 + subOp "Transfer")
            if ts_operationTypeId == 31 and ts_subOperationTypeName == "Transfer":
                ts_transfer_operations_table.append(dict(transaction_row))

            from_vessel = safe_get(transaction.get("fromVessel")) or None
            to_vessel = safe_get(transaction.get("toVessel")) or None

            # Special transfer TO In-Transit-Bldg (op type 47 to in-transit)
            if (
                ts_operationTypeId == 47
                and to_vessel
                and safe_get(to_vessel.get("name"))
                and tanks_lookup.get(safe_get(to_vessel.get("name"))) == intransit_name
            ):
                special_transfer_table.append({
                    "ts_subOperationId": ts_subOperationId,
                    "ts_operationId": safe_get(transaction.get("operationId")),
                    "ts_operationTypeId": ts_operationTypeId,
                    "ts_operationTypeName": safe_get(transaction.get("operationTypeName")),
                    "ts_subOperationTypeName": ts_subOperationTypeName,
                    "ts_formattedDate": safe_get(transaction.get("formattedDate")),
                    "from_ts_name": safe_get(from_vessel.get("name")) if from_vessel else None,
                    "from_ts_vessel_id": safe_get(from_vessel.get("id")) if from_vessel else None,
                    "from_ts_volOut": safe_get(from_vessel.get("volOut")) if from_vessel else None,
                    "from_ts_volOutUnit": safe_get(from_vessel.get("volOutUnit")) if from_vessel else None,
                    "to_ts_name": safe_get(to_vessel.get("name")),
                    "to_ts_vessel_id": safe_get(to_vessel.get("id")),
                    "to_ts_volIn": safe_get(to_vessel.get("volIn")),
                    "to_ts_volInUnit": safe_get(to_vessel.get("volInUnit")),
                })

            # Special transfer FROM In-Transit-Bldg TO NOT In-Transit-Bldg
            if (
                from_vessel
                and safe_get(from_vessel.get("name")) in tanks_lookup
                and tanks_lookup.get(safe_get(from_vessel.get("name"))) == intransit_name
                and to_vessel
                and safe_get(to_vessel.get("name")) in tanks_lookup
                and tanks_lookup.get(safe_get(to_vessel.get("name"))) != intransit_name
            ):
                special_transfer_from_intransit_table.append({
                    "ts_subOperationId": ts_subOperationId,
                    "ts_operationId": safe_get(transaction.get("operationId")),
                    "ts_operationTypeId": ts_operationTypeId,
                    "ts_operationTypeName": safe_get(transaction.get("operationTypeName")),
                    "ts_subOperationTypeName": ts_subOperationTypeName,
                    "ts_formattedDate": safe_get(transaction.get("formattedDate")),
                    "from_ts_name": safe_get(from_vessel.get("name")),
                    "from_ts_vessel_id": safe_get(from_vessel.get("id")),
                    "from_ts_volOut": safe_get(from_vessel.get("volOut")),
                    "from_ts_volOutUnit": safe_get(from_vessel.get("volOutUnit")),
                    "to_ts_name": safe_get(to_vessel.get("name")),
                    "to_ts_vessel_id": safe_get(to_vessel.get("id")),
                    "to_ts_volIn": safe_get(to_vessel.get("volIn")),
                    "to_ts_volInUnit": safe_get(to_vessel.get("volInUnit")),
                })

            # Special transfer FROM In-Transit-Bldg TO In-Transit-Bldg
            if (
                from_vessel
                and safe_get(from_vessel.get("name")) in tanks_lookup
                and tanks_lookup.get(safe_get(from_vessel.get("name"))) == intransit_name
                and to_vessel
                and safe_get(to_vessel.get("name")) in tanks_lookup
                and tanks_lookup.get(safe_get(to_vessel.get("name"))) == intransit_name
            ):
                special_transfer_intransit_to_intransit_table.append({
                    "ts_subOperationId": ts_subOperationId,
                    "ts_operationId": safe_get(transaction.get("operationId")),
                    "ts_operationTypeId": ts_operationTypeId,
                    "ts_operationTypeName": safe_get(transaction.get("operationTypeName")),
                    "ts_subOperationTypeName": ts_subOperationTypeName,
                    "ts_formattedDate": safe_get(transaction.get("formattedDate")),
                    "from_ts_name": safe_get(from_vessel.get("name")),
                    "from_ts_vessel_id": safe_get(from_vessel.get("id")),
                    "from_ts_volOut": safe_get(from_vessel.get("volOut")),
                    "from_ts_volOutUnit": safe_get(from_vessel.get("volOutUnit")),
                    "to_ts_name": safe_get(to_vessel.get("name")),
                    "to_ts_vessel_id": safe_get(to_vessel.get("id")),
                    "to_ts_volIn": safe_get(to_vessel.get("volIn")),
                    "to_ts_volInUnit": safe_get(to_vessel.get("volInUnit")),
                })

            # Vessel tables
            if from_vessel:
                process_vessel_basic("from", from_vessel, ts_subOperationId, from_vessel_seen_ids, ts_transactions_from_vessel_table)
                process_vessel_details(
                    safe_get(from_vessel.get("beforeDetails")),
                    ts_subOperationId,
                    from_vessel_before_details_seen_ids,
                    ts_transactions_from_vessel_before_details_table,
                    ts_batchDetails_vintage_table,
                    ts_batchDetails_variety_table,
                    ts_batchDetails_region_table,
                )
                process_vessel_details(
                    safe_get(from_vessel.get("afterDetails")),
                    ts_subOperationId,
                    from_vessel_after_details_seen_ids,
                    ts_transactions_from_vessel_after_details_table,
                    ts_batchDetails_vintage_table,
                    ts_batchDetails_variety_table,
                    ts_batchDetails_region_table,
                )

            if to_vessel:
                process_vessel_basic("to", to_vessel, ts_subOperationId, to_vessel_seen_ids, ts_transactions_to_vessel_table)
                process_vessel_details(
                    safe_get(to_vessel.get("beforeDetails")),
                    ts_subOperationId,
                    to_vessel_before_details_seen_ids,
                    ts_transactions_to_vessel_before_details_table,
                    ts_batchDetails_vintage_table,
                    ts_batchDetails_variety_table,
                    ts_batchDetails_region_table,
                )
                process_vessel_details(
                    safe_get(to_vessel.get("afterDetails")),
                    ts_subOperationId,
                    to_vessel_after_details_seen_ids,
                    ts_transactions_to_vessel_after_details_table,
                    ts_batchDetails_vintage_table,
                    ts_batchDetails_variety_table,
                    ts_batchDetails_region_table,
                )

            # Loss details
            loss_details = safe_get(transaction.get("lossDetails"))
            if loss_details and ts_subOperationId not in loss_details_seen_ids:
                loss_details_seen_ids.add(ts_subOperationId)
                ts_transactions_loss_details_table.append({
                    "ts_subOperationId": ts_subOperationId,
                    "ts_volume": safe_get(loss_details.get("volume")),
                    "ts_volumeUnit": safe_get(loss_details.get("volumeUnit")),
                    "ts_reason": safe_get(loss_details.get("reason")),
                })

            # Analysis metrics
            analysis_ops = safe_get(transaction.get("analysisOps"))
            if analysis_ops:
                metrics = safe_get(analysis_ops.get("metrics")) or []
                for metric in metrics:
                    key = (ts_subOperationId, safe_get(metric.get("id")))
                    if key in analysis_metrics_seen_keys:
                        continue
                    analysis_metrics_seen_keys.add(key)
                    ts_transactions_analysis_metrics_table.append({
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
                    })

            # Additional details, extraction and grape intake
            additional_details = safe_get(transaction.get("additionalDetails"))
            if additional_details and ts_subOperationId not in additional_details_seen_ids:
                additional_details_seen_ids.add(ts_subOperationId)
                additional_row = {
                    "ts_subOperationId": ts_subOperationId,
                    "ts_summary": flatten_value(safe_get(additional_details.get("summary"))),
                    "ts_bookingNo": flatten_value(safe_get(additional_details.get("bookingNo"))),
                    "ts_owner": flatten_value(safe_get(additional_details.get("owner"))),
                    "ts_netAmountUnit": flatten_value(safe_get(additional_details.get("netAmountUnit"))),
                    "ts_netAmount": flatten_numeric_list(safe_get(additional_details.get("netAmount"))),
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
                }
                trimmed_row = trim_row(additional_row, MAX_LENGTHS["transactions_additional_details"])

                # Extraction table: operationTypeId == 0
                if ts_operationTypeId == 0:
                    ts_extraction_table.append(dict(trimmed_row))
                # Grape intake table: operationTypeId == 4
                if ts_operationTypeId == 4:
                    ts_grape_intake_table.append(dict(trimmed_row))

                ts_transactions_additional_details_table.append(dict(trimmed_row))

                # Extraction parcels
                extraction = safe_get(additional_details.get("extraction"))
                if extraction:
                    parcels = safe_get(extraction.get("parcels")) or []
                    for parcel in parcels:
                        ts_docket_val = safe_get(parcel.get("docket"))
                        if ts_docket_val and ts_docket_val not in extraction_parcels_seen_dockets:
                            extraction_parcels_seen_dockets.add(ts_docket_val)
                            ts_transactions_extraction_parcels_table.append({
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
                            })

            # Addition ops
            addition_ops = safe_get(transaction.get("additionOps"))
            if addition_ops and ts_subOperationId not in addition_ops_seen_ids:
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
                    "ts_lotNumbers": ",".join(safe_get(addition_ops.get("lotNumbers")) or []) if addition_ops.get("lotNumbers") else None,
                }
                additive = safe_get(addition_ops.get("additive"))
                if additive:
                    addition_row.update({
                        "ts_additive_id": safe_get(additive.get("id")),
                        "ts_additive_name": safe_get(additive.get("name")),
                        "ts_additive_description": safe_get(additive.get("description")),
                    })
                ts_transactions_addition_ops_table.append(addition_row)

    # Build special transfer links AFTER all lists are populated
    special_transfer_link_table = build_special_transfer_links(
        special_transfer_table, special_transfer_from_intransit_table, vol_tolerance
    )

    # Update grape_intake_table with extraction fraction fields for matching dockets
    extraction_docket_map: Dict[str, Dict[str, Any]] = {}
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

    # Build unique_dockets_table with merged top-level additional_details fields
    unique_dockets_set: Set[str] = set()
    docket_details_map: Dict[str, Dict[str, Any]] = {}
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
        "ts_fruitProcess",
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

    # Build extracted_gallons table (one per docket, taking toVessel name/volIn from the extraction transaction)
    extracted_gallons_table: List[Dict[str, Any]] = []
    extracted_gallons_dockets_seen: Set[str] = set()

    for row in ts_extraction_table:
        sub_op_id = row.get("ts_subOperationId")
        trans = transactions_by_subOp.get(sub_op_id)
        to_vessel = safe_get(trans.get("toVessel")) if trans else None
        to_vessel_name = safe_get(to_vessel.get("name")) if to_vessel else None
        to_vessel_volIn = safe_get(to_vessel.get("volIn")) if to_vessel else None
        for docket in get_docket_keys(row):
            if docket and docket not in extracted_gallons_dockets_seen:
                extracted_gallons_dockets_seen.add(docket)
                extracted_gallons_table.append({
                    "ts_docket": docket,
                    "toVessel_name": to_vessel_name,
                    "toVessel_volIn": to_vessel_volIn,
                })

    # Split gallons by tonnage among dockets that share the same toVessel
    tonnage_lookup: Dict[str, float] = {}
    for row in unique_dockets_table:
        val = to_float_or_none(row.get("ts_netAmount"))
        tonnage_lookup[row["ts_docket"]] = val if val is not None else 0.0

    grouped: Dict[Tuple[Any, Optional[float]], List[str]] = defaultdict(list)
    for rec in extracted_gallons_table:
        vessel = rec["toVessel_name"]
        volIn = to_float_or_none(rec["toVessel_volIn"])
        grouped[(vessel, volIn)].append(rec["ts_docket"])

    split_gallons_table: List[Dict[str, Any]] = []
    for (vessel, volIn), dockets in grouped.items():
        volIn_val = volIn if volIn is not None else 0.0
        tonnages = [tonnage_lookup.get(d, 0.0) for d in dockets]
        total_tonnage = sum(tonnages)
        for docket, tonnage in zip(dockets, tonnages):
            gallons = (tonnage / total_tonnage * volIn_val) if total_tonnage > 0 and volIn is not None else None
            split_gallons_table.append({
                "ts_docket": docket,
                "toVessel_name": vessel,
                "toVessel_volIn": volIn,
                "allocated_gallons": round(gallons, 2) if gallons is not None else None,
                "ts_netAmount": tonnage,
                "tonnage_total_for_vessel": round(total_tonnage, 2),
            })

    # Master merged output
    unique_dockets_lookup = {row["ts_docket"]: row for row in unique_dockets_table}
    master_table: List[Dict[str, Any]] = []
    for split_row in split_gallons_table:
        docket = split_row["ts_docket"]
        unique_row = unique_dockets_lookup.get(docket, {})
        sub_op_id = unique_row.get("ts_subOperationId") or None
        transaction = transactions_by_subOp.get(sub_op_id)
        transaction_fields: Dict[str, Any] = {}
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
        merged_row = {**unique_row, **split_row, **transaction_fields}
        master_table.append(merged_row)

    # Unique dispatchNos table
    unique_dispatchNos_set: Set[str] = set()
    dispatchNo_details_map: Dict[str, Dict[str, Any]] = {}
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
        "ts_fruitProcess",
    ]
    for row in ts_transactions_additional_details_table:
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

    unique_dispatchNos_table: List[Dict[str, Any]] = []
    for dispatchNo in sorted(unique_dispatchNos_set):
        details = dispatchNo_details_map.get(dispatchNo, {})
        sub_op_id = details.get("ts_subOperationId")
        transaction = transactions_by_subOp.get(sub_op_id)
        transaction_fields: Dict[str, Any] = {}
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

    # --------------------------- Write outputs ---------------------------

    def write_json(path: str, data: Any) -> None:
        with open(path, "w", encoding="utf-8") as f:
            safe_json_dump(data, f)
        logging.info("Wrote %s", path)

    # Special transfers
    write_json(os.path.join(out_dir, "special_transfer_link_table.json"), special_transfer_link_table)
    write_json(os.path.join(out_dir, "special_transfer_intransit_to_intransit_table.json"), special_transfer_intransit_to_intransit_table)
    write_json(os.path.join(out_dir, "special_transfer_from_intransit_table.json"), special_transfer_from_intransit_table)
    write_json(os.path.join(out_dir, "special_transfer_table.json"), special_transfer_table)

    # Transfer ops
    write_json(os.path.join(out_dir, "ts_transfer_operations_table.json"), ts_transfer_operations_table)

    # Transactions and vessel tables
    write_json(os.path.join(out_dir, "ts_transactions.json"), ts_transactions_table)
    write_json(os.path.join(out_dir, "ts_transactions_from_vessel_table.json"), ts_transactions_from_vessel_table)
    write_json(os.path.join(out_dir, "ts_transactions_from_vessel_before_details_table.json"), ts_transactions_from_vessel_before_details_table)
    write_json(os.path.join(out_dir, "ts_transactions_from_vessel_after_details_table.json"), ts_transactions_from_vessel_after_details_table)
    write_json(os.path.join(out_dir, "ts_transactions_to_vessel_table.json"), ts_transactions_to_vessel_table)
    write_json(os.path.join(out_dir, "ts_transactions_to_vessel_before_details_table.json"), ts_transactions_to_vessel_before_details_table)
    write_json(os.path.join(out_dir, "ts_transactions_to_vessel_after_details_table.json"), ts_transactions_to_vessel_after_details_table)
    write_json(os.path.join(out_dir, "ts_transactions_loss_details_table.json"), ts_transactions_loss_details_table)
    write_json(os.path.join(out_dir, "ts_transactions_analysis_metrics_table.json"), ts_transactions_analysis_metrics_table)
    write_json(os.path.join(out_dir, "ts_transactions_additional_details_table.json"), ts_transactions_additional_details_table)
    write_json(os.path.join(out_dir, "ts_transactions_extraction_parcels_table.json"), ts_transactions_extraction_parcels_table)
    write_json(os.path.join(out_dir, "ts_transactions_addition_ops_table.json"), ts_transactions_addition_ops_table)

    # Derived tables
    write_json(os.path.join(out_dir, "ts_extraction_table.json"), ts_extraction_table)
    write_json(os.path.join(out_dir, "ts_grape_intake_table.json"), ts_grape_intake_table)
    write_json(os.path.join(out_dir, "unique_dockets_table.json"), unique_dockets_table)
    write_json(os.path.join(out_dir, "extracted_gallons_table.json"), extracted_gallons_table)
    write_json(os.path.join(out_dir, "split_gallons_table.json"), split_gallons_table)
    write_json(os.path.join(out_dir, "master_table.json"), master_table)
    write_json(os.path.join(out_dir, "unique_dispatchNos_table.json"), unique_dispatchNos_table)

    # ID tables
    write_json(os.path.join(id_out_dir, "ts_batchDetails_vintage_table.json"), list(ts_batchDetails_vintage_table.values()))
    write_json(os.path.join(id_out_dir, "ts_batchDetails_variety_table.json"), list(ts_batchDetails_variety_table.values()))
    write_json(os.path.join(id_out_dir, "ts_batchDetails_region_table.json"), list(ts_batchDetails_region_table.values()))

    # Summary
    logging.info("Split complete! JSON tables written to %s and %s", out_dir, id_out_dir)
    logging.info("Counts: transactions=%d, addl_details=%d, extraction=%d, intake=%d, master=%d",
                 len(ts_transactions_table), len(ts_transactions_additional_details_table),
                 len(ts_extraction_table), len(ts_grape_intake_table), len(master_table))


if __name__ == "__main__":
    main()