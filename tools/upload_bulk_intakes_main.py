# python tools/upload_bulk_intakes_main.py


import json
import os
import pandas as pd
from utils.helpers import safe_get, safe_get_path

JSON_PATH = os.getenv("INTAKES_JSON", "Main/data/GET--intakes/intakes.json")
OUT_DIR = os.getenv("INTAKES_SPLIT_DIR", "Main/data/GET--intakes/tables")
ID_OUT_DIR = "Main/data/id_tables"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ID_OUT_DIR, exist_ok=True)

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

# Tables (all in_ prefix)
in_intakes_table = []
in_composition_table = []
in_cost_table = []
in_ttb_details_table = []
in_delivery_table = []
in_metrics_table = []

# Lookup tables for IDs (deduplication, saved to ID_OUT_DIR)
in_batch_owner_table = {}
in_block_table = {}
in_region_table = {}
in_subRegion_table = {}
in_variety_table = {}
in_bond_table = {}
in_taxClass_table = {}
in_purchaseOrder_table = {}
in_receivedFrom_table = {}
in_carrier_table = {}

with open(JSON_PATH, "r", encoding="utf-8") as f:
    intakes = json.load(f)

for intake in intakes:
    in_intake_id = safe_get(intake.get("id"))
    in_reversed = safe_get(intake.get("reversed"))
    if in_reversed in [True, "true", "True"]:
        continue

    wine_details = safe_get(intake.get("wineDetails"))
    batchOwner_id = safe_get_path(wine_details, ["batchOwner", "id"])
    if batchOwner_id:
        in_batch_owner_table[batchOwner_id] = {
            "in_batchOwner_id": batchOwner_id,
            "in_batchOwner_name": safe_get_path(wine_details, ["batchOwner", "name"]),
            "in_batchOwner_extId": safe_get_path(wine_details, ["batchOwner", "extId"]),
        }

    intake_row = {
        "in_intake_id": in_intake_id,
        "in_id": in_intake_id,
        "in_occurredTime": safe_get(intake.get("occurredTime")),
        "in_reversed": in_reversed,
        "in_vessel": safe_get_path(wine_details, ["vessel"]),
        "in_batch": safe_get_path(wine_details, ["batch"]),
        "in_fractionType": safe_get_path(wine_details, ["fractionType"]),
        "in_fermentState": safe_get_path(wine_details, ["fermentState"]),
        "in_malolacticState": safe_get_path(wine_details, ["malolacticState"]),
        "in_productType": safe_get_path(wine_details, ["productType"]),
        "in_beverageType": safe_get_path(wine_details, ["beverageType"]),
        "in_reference": safe_get_path(wine_details, ["reference"]),
        "in_yieldRate": safe_get_path(wine_details, ["yieldRate"]),
        "in_volume_unit": safe_get_path(wine_details, ["volume", "unit"]),
        "in_volume_value": safe_get_path(wine_details, ["volume", "value"]),
        "in_batchOwner_id": batchOwner_id,
    }
    in_intakes_table.append(intake_row)

    # --- Composition Table ---
    compositions = safe_get(intake.get("composition")) or []
    in_volume_value = safe_get_path(wine_details, ["volume", "value"])
    for idx, composition in enumerate(compositions):
        perc = safe_get(composition.get("percentage"))
        in_CompGal = None
        if in_volume_value is not None and perc is not None:
            try:
                in_CompGal = float(in_volume_value) * float(perc) / 100
            except Exception:
                in_CompGal = None
        block_id = safe_get_path(composition, ["block", "id"])
        if block_id:
            in_block_table[block_id] = {
                "in_block_id": block_id,
                "in_block_name": safe_get_path(composition, ["block", "name"]),
                "in_block_extId": safe_get_path(composition, ["block", "extId"]),
            }
        region_id = safe_get_path(composition, ["region", "id"])
        if region_id:
            in_region_table[region_id] = {
                "in_region_id": region_id,
                "in_region_name": safe_get_path(composition, ["region", "name"]),
            }
        subRegion_id = safe_get_path(composition, ["subRegion", "id"])
        if subRegion_id:
            in_subRegion_table[subRegion_id] = {
                "in_subRegion_id": subRegion_id,
                "in_subRegion_name": safe_get_path(composition, ["subRegion", "name"]),
            }
        variety_id = safe_get_path(composition, ["variety", "id"])
        if variety_id:
            in_variety_table[variety_id] = {
                "in_variety_id": variety_id,
                "in_variety_name": safe_get_path(composition, ["variety", "name"]),
            }
        composition_row = {
            "in_composition_id": f"{in_intake_id}_{idx}",
            "in_intake_id": in_intake_id,
            "in_percentage": perc,
            "in_vintage": safe_get(composition.get("vintage")),
            "in_block_id": block_id,
            "in_region_id": region_id,
            "in_subRegion_id": subRegion_id,
            "in_variety_id": variety_id,
            "in_CompGal": in_CompGal,
        }
        in_composition_table.append(composition_row)

    # --- Cost Table ---
    cost = safe_get(intake.get("cost"))
    if cost:
        cost_row = {
            "in_cost_id": in_intake_id,
            "in_intake_id": in_intake_id,
            "in_amount": safe_get(cost.get("amount")),
            "in_rate": safe_get(cost.get("rate")),
            "in_freight": safe_get(cost.get("freight")),
        }
        in_cost_table.append(cost_row)

        ttb = safe_get(cost.get("ttbDetails"))
        if ttb:
            bond_id = safe_get_path(ttb, ["bond", "id"])
            if bond_id:
                in_bond_table[bond_id] = {
                    "in_bond_id": bond_id,
                    "in_bond_name": safe_get_path(ttb, ["bond", "name"]),
                }
            taxClass_id = safe_get_path(ttb, ["taxClass", "id"])
            if taxClass_id:
                in_taxClass_table[taxClass_id] = {
                    "in_taxClass_id": taxClass_id,
                    "in_taxClass_name": safe_get_path(ttb, ["taxClass", "name"]),
                }
            ttb_row = {
                "in_ttb_id": in_intake_id,
                "in_intake_id": in_intake_id,
                "in_bond_id": bond_id,
                "in_taxState": safe_get(ttb.get("taxState")),
                "in_taxClass_id": taxClass_id,
                "in_alcoholPercentage": safe_get(ttb.get("alcoholPercentage")),
            }
            in_ttb_details_table.append(ttb_row)

    # --- Delivery Table ---
    delivery = safe_get(intake.get("deliveryDetails"))
    if delivery:
        purchaseOrder_id = safe_get_path(delivery, ["purchaseOrder", "id"])
        if purchaseOrder_id:
            in_purchaseOrder_table[purchaseOrder_id] = {
                "in_purchaseOrder_id": purchaseOrder_id,
                "in_purchaseOrder_name": safe_get_path(delivery, ["purchaseOrder", "name"]),
            }
        receivedFrom_id = safe_get_path(delivery, ["receivedFrom", "id"])
        if receivedFrom_id:
            in_receivedFrom_table[receivedFrom_id] = {
                "in_receivedFrom_id": receivedFrom_id,
                "in_receivedFrom_name": safe_get_path(delivery, ["receivedFrom", "name"]),
            }
        carrier_id = safe_get_path(delivery, ["carrier", "id"])
        if carrier_id:
            in_carrier_table[carrier_id] = {
                "in_carrier_id": carrier_id,
                "in_carrier_name": safe_get_path(delivery, ["carrier", "name"]),
            }
        delivery_row = {
            "in_delivery_id": in_intake_id,
            "in_intake_id": in_intake_id,
            "in_purchaseOrder_id": purchaseOrder_id,
            "in_receivedFrom_id": receivedFrom_id,
            "in_carrier_id": carrier_id,
            "in_shippingRefNo": safe_get(delivery.get("shippingRefNo")),
            "in_truckNo": safe_get(delivery.get("truckNo")),
            "in_driverName": safe_get(delivery.get("driverName")),
            "in_sealNo": safe_get(delivery.get("sealNo")),
            "in_compartmentNo": safe_get(delivery.get("compartmentNo")),
            "in_cipNo": safe_get(delivery.get("cipNo")),
            "in_container": safe_get(delivery.get("container")),
            "in_customsEntryNumber": safe_get(delivery.get("customsEntryNumber")),
            "in_purchaseReference": safe_get(delivery.get("purchaseReference")),
            "in_deliveryState": safe_get(delivery.get("deliveryState")),
        }
        in_delivery_table.append(delivery_row)

    # --- Metrics Table ---
    metrics = safe_get(intake.get("metrics")) or []
    for idx, metric in enumerate(metrics):
        metric_row = {
            "in_metric_id": f"{in_intake_id}_{idx}",
            "in_intake_id": in_intake_id,
            "in_metric_name": safe_get(metric.get("name")),
            "in_metric_value": safe_get(metric.get("value")),
            "in_metric_nonNumericValue": safe_get(metric.get("nonNumericValue")),
            "in_metric_interfaceMappedName": safe_get(metric.get("interfaceMappedName")),
        }
        in_metrics_table.append(metric_row)

# --- Write to JSON files ---
safe_json_dump(in_intakes_table, open(os.path.join(OUT_DIR, "in_intakes.json"), "w", encoding="utf-8"))
safe_json_dump(in_composition_table, open(os.path.join(OUT_DIR, "in_composition.json"), "w", encoding="utf-8"))
safe_json_dump(in_cost_table, open(os.path.join(OUT_DIR, "in_cost.json"), "w", encoding="utf-8"))
safe_json_dump(in_ttb_details_table, open(os.path.join(OUT_DIR, "in_ttb_details.json"), "w", encoding="utf-8"))
safe_json_dump(in_delivery_table, open(os.path.join(OUT_DIR, "in_delivery.json"), "w", encoding="utf-8"))
safe_json_dump(in_metrics_table, open(os.path.join(OUT_DIR, "in_metrics.json"), "w", encoding="utf-8"))

# --- Write ID tables to ID_OUT_DIR ---
safe_json_dump(list(in_batch_owner_table.values()), open(os.path.join(ID_OUT_DIR, "in_batch_owner.json"), "w", encoding="utf-8"))
safe_json_dump(list(in_block_table.values()), open(os.path.join(ID_OUT_DIR, "in_block.json"), "w", encoding="utf-8"))
safe_json_dump(list(in_region_table.values()), open(os.path.join(ID_OUT_DIR, "in_region.json"), "w", encoding="utf-8"))
safe_json_dump(list(in_subRegion_table.values()), open(os.path.join(ID_OUT_DIR, "in_subRegion.json"), "w", encoding="utf-8"))
safe_json_dump(list(in_variety_table.values()), open(os.path.join(ID_OUT_DIR, "in_variety.json"), "w", encoding="utf-8"))
safe_json_dump(list(in_bond_table.values()), open(os.path.join(ID_OUT_DIR, "in_bond.json"), "w", encoding="utf-8"))
safe_json_dump(list(in_taxClass_table.values()), open(os.path.join(ID_OUT_DIR, "in_taxClass.json"), "w", encoding="utf-8"))
safe_json_dump(list(in_purchaseOrder_table.values()), open(os.path.join(ID_OUT_DIR, "in_purchaseOrder.json"), "w", encoding="utf-8"))
safe_json_dump(list(in_receivedFrom_table.values()), open(os.path.join(ID_OUT_DIR, "in_receivedFrom.json"), "w", encoding="utf-8"))
safe_json_dump(list(in_carrier_table.values()), open(os.path.join(ID_OUT_DIR, "in_carrier.json"), "w", encoding="utf-8"))

print("Split complete! JSON tables written to", OUT_DIR, "and", ID_OUT_DIR)