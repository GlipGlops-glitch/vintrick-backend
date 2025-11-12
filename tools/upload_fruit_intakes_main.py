#python tools/upload_fruit_intakes_main.py

import json
import os

from utils.helpers import safe_get_path, safe_get

JSON_PATH = os.getenv("FRUIT_INTAKES_JSON", "Main/data/GET--fruit_intakes/fruit_intakes.json")
OUT_DIR = os.getenv("FRUIT_INTAKES_SPLIT_DIR", "Main/data/GET--fruit_intakes/tables")
ID_OUT_DIR = "Main/data/id_tables"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ID_OUT_DIR, exist_ok=True)

fr_fruit_intakes_table = []
fr_fruit_intakes_metrics_table = []

# Lookup tables for deduplication
fr_blocks_table = {}
fr_vineyards_table = {}
fr_wineries_table = {}
fr_growers_table = {}
fr_regions_table = {}
fr_varieties_table = {}
fr_owners_table = {}
fr_grower_contracts_table = {}

with open(JSON_PATH, "r", encoding="utf-8") as f:
    fruit_intakes = json.load(f)

for intake in fruit_intakes:
    fr_intake_id = safe_get(intake.get("id"))
    fr_reversed = safe_get(intake.get("reversed"))
    # Only collect if not reversed (False or "False")
    if fr_reversed in [True, "true", "True"]:
        continue

    # --- Deduplicate child tables ---
    block = intake.get("block")
    block_id = safe_get_path(block, ["id"])
    if block_id:
        fr_blocks_table[block_id] = {
            "fr_block_id": block_id,
            "fr_block_name": safe_get_path(block, ["name"]),
            "fr_block_externalCode": safe_get_path(block, ["externalCode"])
        }

    vineyard = intake.get("vineyard")
    vineyard_id = safe_get_path(vineyard, ["id"])
    if vineyard_id:
        fr_vineyards_table[vineyard_id] = {
            "fr_vineyard_id": vineyard_id,
            "fr_vineyard_name": safe_get_path(vineyard, ["name"])
        }

    winery = intake.get("winery")
    winery_id = safe_get_path(winery, ["id"])
    if winery_id:
        fr_wineries_table[winery_id] = {
            "fr_winery_id": winery_id,
            "fr_winery_name": safe_get_path(winery, ["name"])
        }

    grower = intake.get("grower")
    grower_id = safe_get_path(grower, ["id"])
    if grower_id:
        fr_growers_table[grower_id] = {
            "fr_grower_id": grower_id,
            "fr_grower_name": safe_get_path(grower, ["name"])
        }

    region = intake.get("region")
    region_id = safe_get_path(region, ["id"])
    if region_id:
        fr_regions_table[region_id] = {
            "fr_region_id": region_id,
            "fr_region_name": safe_get_path(region, ["name"]),
            "fr_region_shortCode": safe_get_path(region, ["shortCode"])
        }

    variety = intake.get("variety")
    variety_id = safe_get_path(variety, ["id"])
    if variety_id:
        fr_varieties_table[variety_id] = {
            "fr_variety_id": variety_id,
            "fr_variety_name": safe_get_path(variety, ["name"]),
            "fr_variety_shortCode": safe_get_path(variety, ["shortCode"])
        }

    owner = intake.get("owner")
    owner_id = safe_get_path(owner, ["id"])
    if owner_id:
        fr_owners_table[owner_id] = {
            "fr_owner_id": owner_id,
            "fr_owner_name": safe_get_path(owner, ["name"]),
            "fr_owner_shortCode": safe_get_path(owner, ["shortCode"])
        }

    grower_contract = intake.get("growerContract")
    grower_contract_id = safe_get_path(grower_contract, ["id"])
    if grower_contract_id:
        fr_grower_contracts_table[grower_contract_id] = {
            "fr_growerContract_id": grower_contract_id,
            "fr_growerContract_name": safe_get_path(grower_contract, ["name"])
        }

    # --- Fruit Intakes Table ---
    intake_row = {
        "fr_intake_id": fr_intake_id,
        "fr_operationId": safe_get(intake.get("operationId")),
        "fr_processId": safe_get(intake.get("processId")),
        "fr_reversed": fr_reversed,
        "fr_effectiveDate": safe_get(intake.get("effectiveDate")),
        "fr_modified": safe_get(intake.get("modified")),
        "fr_bookingNumber": safe_get(intake.get("bookingNumber")),
        "fr_block_id": block_id,
        "fr_vineyard_id": vineyard_id,
        "fr_winery_id": winery_id,
        "fr_grower_id": grower_id,
        "fr_region_id": region_id,
        "fr_variety_id": variety_id,
        "fr_owner_id": owner_id,
        "fr_growerContract_id": grower_contract_id,
        "fr_vintage": safe_get(intake.get("vintage")),
        "fr_deliveryStart": safe_get(intake.get("deliveryStart")),
        "fr_deliveryEnd": safe_get(intake.get("deliveryEnd")),
        "fr_driverName": safe_get(intake.get("driverName")),
        "fr_truckRegistration": safe_get(intake.get("truckRegistration")),
        "fr_carrier": safe_get(intake.get("carrier")),
        "fr_consignmentNote": safe_get(intake.get("consignmentNote")),
        "fr_docketNo": safe_get(intake.get("docketNo")),
        "fr_amount_value": safe_get_path(intake, ["amount", "value"]),
        "fr_amount_unit": safe_get_path(intake, ["amount", "unit"]),
        "fr_grossAmount_value": safe_get_path(intake, ["grossAmount", "value"]),
        "fr_grossAmount_unit": safe_get_path(intake, ["grossAmount", "unit"]),
        "fr_tareAmount_value": safe_get_path(intake, ["tareAmount", "value"]),
        "fr_tareAmount_unit": safe_get_path(intake, ["tareAmount", "unit"]),
        "fr_mog": safe_get(intake.get("mog")),
        "fr_harvestMethod": safe_get(intake.get("harvestMethod")),
        "fr_intendedUse": safe_get(intake.get("intendedUse")),
        "fr_fruitCost": safe_get(intake.get("fruitCost")),
        "fr_fruitCostRateType": safe_get(intake.get("fruitCostRateType")),
        "fr_area": safe_get(intake.get("area")),
        "fr_lastLoad": safe_get(intake.get("lastLoad")),
        "fr_externalWeighTag": safe_get(intake.get("externalWeighTag")),
        "fr_additionalDetails": safe_get(intake.get("additionalDetails")),
    }
    fr_fruit_intakes_table.append(intake_row)

    # --- Metrics Table ---
    metrics = safe_get(intake.get("metrics")) or []
    for metric in metrics:
        metric_row = {
            "fr_metric_id": safe_get(metric.get("metricId")),
            "fr_intake_id": fr_intake_id,
            "fr_metricName": safe_get(metric.get("metricName")),
            "fr_metricShortCode": safe_get(metric.get("metricShortCode")),
            "fr_metric_value": safe_get(metric.get("value")),
            "fr_metric_unit": safe_get(metric.get("unit")),
            "fr_metric_recorded": safe_get(metric.get("recorded")),
            "fr_metricId": safe_get(metric.get("metricId")),
        }
        fr_fruit_intakes_metrics_table.append(metric_row)

# --- Write to JSON files ---
with open(os.path.join(OUT_DIR, "fr_fruit_intakes.json"), "w", encoding="utf-8") as f:
    json.dump(fr_fruit_intakes_table, f, indent=2)

with open(os.path.join(OUT_DIR, "fr_fruit_intakes_metrics.json"), "w", encoding="utf-8") as f:
    json.dump(fr_fruit_intakes_metrics_table, f, indent=2)

with open(os.path.join(ID_OUT_DIR, "fr_blocks.json"), "w", encoding="utf-8") as f:
    json.dump(list(fr_blocks_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "fr_vineyards.json"), "w", encoding="utf-8") as f:
    json.dump(list(fr_vineyards_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "fr_wineries.json"), "w", encoding="utf-8") as f:
    json.dump(list(fr_wineries_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "fr_growers.json"), "w", encoding="utf-8") as f:
    json.dump(list(fr_growers_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "fr_regions.json"), "w", encoding="utf-8") as f:
    json.dump(list(fr_regions_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "fr_varieties.json"), "w", encoding="utf-8") as f:
    json.dump(list(fr_varieties_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "fr_owners.json"), "w", encoding="utf-8") as f:
    json.dump(list(fr_owners_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "fr_grower_contracts.json"), "w", encoding="utf-8") as f:
    json.dump(list(fr_grower_contracts_table.values()), f, indent=2)

print("Split complete! JSON tables written to", OUT_DIR, "and", ID_OUT_DIR)