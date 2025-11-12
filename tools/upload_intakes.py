# python tools/upload_intakes.py


import json
import os
import uuid

from utils.helpers import safe_get_path, safe_get

JSON_PATH = os.getenv("INTAKES_JSON", "Main/data/GET--intakes/intakes.json")
OUT_DIR = os.getenv("INTAKES_SPLIT_DIR", "Main/data/GET--intakes/tables")
os.makedirs(OUT_DIR, exist_ok=True)

def generate_uid():
    return str(uuid.uuid4())

with open(JSON_PATH, "r", encoding="utf-8") as f:
    intakes = json.load(f)

intakes_table = []
intakes_composition_table = []
intakes_cost_table = []
intakes_ttb_details_table = []
intakes_delivery_table = []
intakes_metrics_table = []

for intake in intakes:
    in_intake_id = generate_uid()
    # --- Intakes Table ---
    wine_details = safe_get(intake.get("wineDetails"))
    intake_row = {
        "in_intake_id": in_intake_id,
        "in_id": safe_get(intake.get("id")),
        "in_occurredTime": safe_get(intake.get("occurredTime")),
        "in_reversed": safe_get(intake.get("reversed")),
        # wineDetails (flattened)
        "in_vessel": safe_get_path(wine_details, ["vessel"]),
        "in_batch": safe_get_path(wine_details, ["batch"]),
        "in_fractionType": safe_get_path(wine_details, ["fractionType"]),
        "in_fermentState": safe_get_path(wine_details, ["fermentState"]),
        "in_malolacticState": safe_get_path(wine_details, ["malolacticState"]),
        "in_productType": safe_get_path(wine_details, ["productType"]),
        "in_beverageType": safe_get_path(wine_details, ["beverageType"]),
        "in_reference": safe_get_path(wine_details, ["reference"]),
        "in_yieldRate": safe_get_path(wine_details, ["yieldRate"]),
        # volume
        "in_volume_unit": safe_get_path(wine_details, ["volume", "unit"]),
        "in_volume_value": safe_get_path(wine_details, ["volume", "value"]),
        # batchOwner
        "in_batchOwner_id": safe_get_path(wine_details, ["batchOwner", "id"]),
        "in_batchOwner_name": safe_get_path(wine_details, ["batchOwner", "name"]),
        "in_batchOwner_extId": safe_get_path(wine_details, ["batchOwner", "extId"]),
    }
    intakes_table.append(intake_row)

    # --- Ownership Table (optional: if you want a separate table for each owner)
    # Could be added here if needed

    # --- Composition Table ---
    compositions = safe_get(intake.get("composition")) or []
    in_volume_value = safe_get_path(wine_details, ["volume", "value"])
    for composition in compositions:
        in_composition_id = generate_uid()
        perc = safe_get(composition.get("percentage"))
        in_CompGal = None
        if in_volume_value is not None and perc is not None:
            try:
                in_CompGal = float(in_volume_value) * float(perc) / 100
            except Exception:
                in_CompGal = None
        composition_row = {
            "in_composition_id": in_composition_id,
            "in_intake_id": in_intake_id,
            "in_percentage": perc,
            "in_vintage": safe_get(composition.get("vintage")),
            "in_block_id": safe_get_path(composition, ["block", "id"]),
            "in_block_name": safe_get_path(composition, ["block", "name"]),
            "in_block_extId": safe_get_path(composition, ["block", "extId"]),
            "in_region_id": safe_get_path(composition, ["region", "id"]),
            "in_region_name": safe_get_path(composition, ["region", "name"]),
            "in_subRegion_id": safe_get_path(composition, ["subRegion", "id"]),
            "in_subRegion_name": safe_get_path(composition, ["subRegion", "name"]),
            "in_variety_id": safe_get_path(composition, ["variety", "id"]),
            "in_variety_name": safe_get_path(composition, ["variety", "name"]),
            "in_CompGal": in_CompGal,
        }
        intakes_composition_table.append(composition_row)

    # --- Cost Table ---
    cost = safe_get(intake.get("cost"))
    if cost:
        in_cost_id = generate_uid()
        intake_row["in_cost_id"] = in_cost_id
        cost_row = {
            "in_cost_id": in_cost_id,
            "in_intake_id": in_intake_id,
            "in_amount": safe_get(cost.get("amount")),
            "in_rate": safe_get(cost.get("rate")),
            "in_freight": safe_get(cost.get("freight")),
        }
        intakes_cost_table.append(cost_row)

        ttb = safe_get(cost.get("ttbDetails"))
        if ttb:
            in_ttb_id = generate_uid()
            intake_row["in_ttb_id"] = in_ttb_id
            ttb_row = {
                "in_ttb_id": in_ttb_id,
                "in_intake_id": in_intake_id,
                "in_bond_id": safe_get_path(ttb, ["bond", "id"]),
                "in_bond_name": safe_get_path(ttb, ["bond", "name"]),
                "in_taxState": safe_get(ttb.get("taxState")),
                "in_taxClass_id": safe_get_path(ttb, ["taxClass", "id"]),
                "in_taxClass_name": safe_get_path(ttb, ["taxClass", "name"]),
                "in_taxClass_federalName": safe_get_path(ttb, ["taxClass", "federalName"]),
                "in_taxClass_stateName": safe_get_path(ttb, ["taxClass", "stateName"]),
                "in_alcoholPercentage": safe_get(ttb.get("alcoholPercentage")),
            }
            intakes_ttb_details_table.append(ttb_row)

    # --- Delivery Table ---
    delivery = safe_get(intake.get("deliveryDetails"))
    if delivery:
        in_delivery_id = generate_uid()
        intake_row["in_delivery_id"] = in_delivery_id
        delivery_row = {
            "in_delivery_id": in_delivery_id,
            "in_intake_id": in_intake_id,
            "in_purchaseOrder_id": safe_get_path(delivery, ["purchaseOrder", "id"]),
            "in_purchaseOrder_name": safe_get_path(delivery, ["purchaseOrder", "name"]),
            "in_receivedFrom_id": safe_get_path(delivery, ["receivedFrom", "id"]),
            "in_receivedFrom_name": safe_get_path(delivery, ["receivedFrom", "name"]),
            "in_carrier_id": safe_get_path(delivery, ["carrier", "id"]),
            "in_carrier_name": safe_get_path(delivery, ["carrier", "name"]),
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
        intakes_delivery_table.append(delivery_row)

    # --- Metrics Table ---
    metrics = safe_get(intake.get("metrics")) or []
    for metric in metrics:
        in_metric_id = generate_uid()
        metric_row = {
            "in_metric_id": in_metric_id,
            "in_intake_id": in_intake_id,
            "in_metric_name": safe_get(metric.get("name")),
            "in_metric_value": safe_get(metric.get("value")),
            "in_metric_nonNumericValue": safe_get(metric.get("nonNumericValue")),
            "in_metric_interfaceMappedName": safe_get(metric.get("interfaceMappedName")),
        }
        intakes_metrics_table.append(metric_row)

# --- Write to JSON files ---
with open(os.path.join(OUT_DIR, "intakes.json"), "w", encoding="utf-8") as f:
    json.dump(intakes_table, f, indent=2)

with open(os.path.join(OUT_DIR, "intakes_composition.json"), "w", encoding="utf-8") as f:
    json.dump(intakes_composition_table, f, indent=2)

with open(os.path.join(OUT_DIR, "intakes_cost.json"), "w", encoding="utf-8") as f:
    json.dump(intakes_cost_table, f, indent=2)

with open(os.path.join(OUT_DIR, "intakes_ttb_details.json"), "w", encoding="utf-8") as f:
    json.dump(intakes_ttb_details_table, f, indent=2)

with open(os.path.join(OUT_DIR, "intakes_delivery.json"), "w", encoding="utf-8") as f:
    json.dump(intakes_delivery_table, f, indent=2)

with open(os.path.join(OUT_DIR, "intakes_metrics.json"), "w", encoding="utf-8") as f:
    json.dump(intakes_metrics_table, f, indent=2)

print("Split complete! JSON tables written to", OUT_DIR)