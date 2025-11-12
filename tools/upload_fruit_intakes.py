#python tools/upload_fruit_intakes.py

import json
import os

from utils.helpers import safe_get_path, safe_get

JSON_PATH = os.getenv("FRUIT_INTAKES_JSON", "Main/data/GET--fruit_intakes/fruit_intakes.json")
OUT_DIR = os.getenv("FRUIT_INTAKES_SPLIT_DIR", "Main/data/GET--fruit_intakes/tables")
os.makedirs(OUT_DIR, exist_ok=True)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    fruit_intakes = json.load(f)

fruit_intakes_table = []
fruit_intakes_metrics_table = []

for intake in fruit_intakes:
    fi_intake_id = safe_get(intake.get("id"))
    # --- Fruit Intakes Table ---
    intake_row = {
        "fi_intake_id": fi_intake_id,
        "fi_operationId": safe_get(intake.get("operationId")),
        "fi_processId": safe_get(intake.get("processId")),
        "fi_reversed": safe_get(intake.get("reversed")),
        "fi_effectiveDate": safe_get(intake.get("effectiveDate")),
        "fi_modified": safe_get(intake.get("modified")),
        "fi_bookingNumber": safe_get(intake.get("bookingNumber")),
        "fi_vintage": safe_get(intake.get("vintage")),
        "fi_deliveryStart": safe_get(intake.get("deliveryStart")),
        "fi_deliveryEnd": safe_get(intake.get("deliveryEnd")),
        "fi_driverName": safe_get(intake.get("driverName")),
        "fi_truckRegistration": safe_get(intake.get("truckRegistration")),
        "fi_carrier": safe_get(intake.get("carrier")),
        "fi_consignmentNote": safe_get(intake.get("consignmentNote")),
        "fi_docketNo": safe_get(intake.get("docketNo")),
        "fi_amount_value": safe_get_path(intake, ["amount", "value"]),
        "fi_amount_unit": safe_get_path(intake, ["amount", "unit"]),
        "fi_grossAmount_value": safe_get_path(intake, ["grossAmount", "value"]),
        "fi_grossAmount_unit": safe_get_path(intake, ["grossAmount", "unit"]),
        "fi_tareAmount_value": safe_get_path(intake, ["tareAmount", "value"]),
        "fi_tareAmount_unit": safe_get_path(intake, ["tareAmount", "unit"]),
        "fi_mog": safe_get(intake.get("mog")),
        "fi_harvestMethod": safe_get(intake.get("harvestMethod")),
        "fi_intendedUse": safe_get(intake.get("intendedUse")),
        "fi_fruitCost": safe_get(intake.get("fruitCost")),
        "fi_fruitCostRateType": safe_get(intake.get("fruitCostRateType")),
        "fi_area": safe_get(intake.get("area")),
        "fi_lastLoad": safe_get(intake.get("lastLoad")),
        "fi_externalWeighTag": safe_get(intake.get("externalWeighTag")),
        "fi_additionalDetails": safe_get(intake.get("additionalDetails")),


        "fi_block_id": safe_get_path(intake, ["block", "id"]),
        "fi_block_name": safe_get_path(intake, ["block", "name"]),
        "fi_block_externalCode": safe_get_path(intake, ["block", "externalCode"]),
        "fi_vineyard_id": safe_get_path(intake, ["vineyard", "id"]),
        "fi_vineyard_name": safe_get_path(intake, ["vineyard", "name"]),
        "fi_winery_id": safe_get_path(intake, ["winery", "id"]),
        "fi_winery_name": safe_get_path(intake, ["winery", "name"]),
        "fi_grower_id": safe_get_path(intake, ["grower", "id"]),
        "fi_grower_name": safe_get_path(intake, ["grower", "name"]),
        "fi_region_id": safe_get_path(intake, ["region", "id"]),
        "fi_region_name": safe_get_path(intake, ["region", "name"]),
        "fi_region_shortCode": safe_get_path(intake, ["region", "shortCode"]),
        "fi_variety_id": safe_get_path(intake, ["variety", "id"]),
        "fi_variety_name": safe_get_path(intake, ["variety", "name"]),
        "fi_variety_shortCode": safe_get_path(intake, ["variety", "shortCode"]),
        "fi_owner_id": safe_get_path(intake, ["owner", "id"]),
        "fi_owner_name": safe_get_path(intake, ["owner", "name"]),
        "fi_owner_shortCode": safe_get_path(intake, ["owner", "shortCode"]),
        "fi_growerContract_id": safe_get_path(intake, ["growerContract", "id"]),
        "fi_growerContract_name": safe_get_path(intake, ["growerContract", "name"]),
    }
    fruit_intakes_table.append(intake_row)
    

    # --- Metrics Table ---
    metrics = safe_get(intake.get("metrics")) or []
    for metric in metrics:
        metric_row = {
            "fi_metric_id": safe_get(metric.get("metricId")),
            "fi_intake_id": fi_intake_id,
            "fi_metricName": safe_get(metric.get("metricName")),
            "fi_metricShortCode": safe_get(metric.get("metricShortCode")),
            "fi_metric_value": safe_get(metric.get("value")),
            "fi_metric_unit": safe_get(metric.get("unit")),
            "fi_metric_recorded": safe_get(metric.get("recorded")),
            "fi_metricId": safe_get(metric.get("metricId")),
        }
        fruit_intakes_metrics_table.append(metric_row)

# --- Write to JSON files ---
with open(os.path.join(OUT_DIR, "fruit_intakes.json"), "w", encoding="utf-8") as f:
    json.dump(fruit_intakes_table, f, indent=2)

with open(os.path.join(OUT_DIR, "fruit_intakes_metrics.json"), "w", encoding="utf-8") as f:
    json.dump(fruit_intakes_metrics_table, f, indent=2)

print("Split complete! JSON tables written to", OUT_DIR)