# python tools/upload_shipments_short.py
# Refactored: Splits flattened shipments JSON into normalized tables as separate JSON files
# Now adds 'CompGal' to composition table as volume_value * (percentage / 100)

import json
import os
import uuid

JSON_PATH = os.getenv("SHIPMENTS_JSON", "Main/data/GET--shipments/all_shipments.json")
OUT_DIR = os.getenv("SHIPMENTS_SPLIT_DIR", "Main/data/GET--shipments/tables")
os.makedirs(OUT_DIR, exist_ok=True)

def generate_uid():
    return str(uuid.uuid4())

with open(JSON_PATH, "r", encoding="utf-8") as f:
    shipments = json.load(f)

shipments_table = []
wine_details_table = []
wine_batch_table = []
composition_table = []

for shipment in shipments:
    shipment_id = generate_uid()

    # --- Shipment Table ---
    shipment_row = {
        "shipment_id": shipment_id,
        "id": shipment.get("id"),
        "workOrderNumber": shipment.get("workOrderNumber"),
        "jobNumber": shipment.get("jobNumber"),
        "shipmentNumber": shipment.get("shipmentNumber"),
        "type": shipment.get("type"),
        "occurredTime": shipment.get("occurredTime"),
        "modifiedTime": shipment.get("modifiedTime"),
        "reference": shipment.get("reference"),
        "freightCode": shipment.get("freightCode"),
        "reversed": shipment.get("reversed"),
        "source_id": shipment.get("source", {}).get("id"),
        "source_name": shipment.get("source", {}).get("name"),
        "source_businessUnit": shipment.get("source", {}).get("businessUnit"),
        "destination_winery_name": shipment.get("destination", {}).get("winery", {}).get("name")
            if isinstance(shipment.get("destination", {}).get("winery"), dict) else None,
        "destination_party_id": shipment.get("destination", {}).get("party", {}).get("id")
            if isinstance(shipment.get("destination", {}).get("party"), dict) else None,
        "destination_party_name": shipment.get("destination", {}).get("party", {}).get("name")
            if isinstance(shipment.get("destination", {}).get("party"), dict) else None,
        "carrier": shipment.get("carrier", {}).get("name")
            if isinstance(shipment.get("carrier"), dict) else shipment.get("carrier"),
        "dispatchType_id": shipment.get("dispatchType", {}).get("id")
            if isinstance(shipment.get("dispatchType"), dict) else None,
        "dispatchType_name": shipment.get("dispatchType", {}).get("name")
            if isinstance(shipment.get("dispatchType"), dict) else None
    }
    shipments_table.append(shipment_row)

    # --- Wine Details Table ---
    wine_details = shipment.get("wineDetails", [])
    for wine_detail in wine_details:
        wine_details_id = generate_uid()

        wine_details_row = {
            "wine_details_id": wine_details_id,
            "shipment_id": shipment_id,
            "vessel": wine_detail.get("vessel"),
            "batch": wine_detail.get("batch"),
            "weight": wine_detail.get("weight"),
            "volume_unit": wine_detail.get("volume", {}).get("unit") if wine_detail.get("volume") else None,
            "volume_value": wine_detail.get("volume", {}).get("value") if wine_detail.get("volume") else None,
            "loss_volume_unit": wine_detail.get("loss", {}).get("volume", {}).get("unit")
                if wine_detail.get("loss") and wine_detail.get("loss", {}).get("volume") else None,
            "loss_volume_value": wine_detail.get("loss", {}).get("volume", {}).get("value")
                if wine_detail.get("loss") and wine_detail.get("loss", {}).get("volume") else None,
            "loss_reason_id": wine_detail.get("loss", {}).get("reason", {}).get("id")
                if wine_detail.get("loss") and wine_detail.get("loss", {}).get("reason") else None,
            "loss_reason_name": wine_detail.get("loss", {}).get("reason", {}).get("name")
                if wine_detail.get("loss") and wine_detail.get("loss", {}).get("reason") else None,
            "bottlingDetails": wine_detail.get("bottlingDetails"),
            "wineryBuilding_id": wine_detail.get("wineryBuilding", {}).get("id")
                if isinstance(wine_detail.get("wineryBuilding"), dict) else None,
            "wineryBuilding_name": wine_detail.get("wineryBuilding", {}).get("name")
                if isinstance(wine_detail.get("wineryBuilding"), dict) else None,
        }
        wine_details_table.append(wine_details_row)

        # --- Wine Batch Table ---
        wine_batch = wine_detail.get("wineBatch", {})
        if wine_batch:
            wine_batch_id = generate_uid()
            wine_details_row["wine_batch_id"] = wine_batch_id
            wine_batch_row = {
                "wine_batch_id": wine_batch_id,
                "wine_details_id": wine_details_id,
                "id": wine_batch.get("id"),
                "name": wine_batch.get("name"),
                "description": wine_batch.get("description"),
                "vintage": wine_batch.get("vintage"),
                "program": wine_batch.get("program"),
                "designatedRegion_id": wine_batch.get("designatedRegion", {}).get("id")
                    if "designatedRegion" in wine_batch and isinstance(wine_batch.get("designatedRegion"), dict) else None,
                "designatedRegion_name": wine_batch.get("designatedRegion", {}).get("name")
                    if "designatedRegion" in wine_batch and isinstance(wine_batch.get("designatedRegion"), dict) else None,
                "designatedRegion_code": wine_batch.get("designatedRegion", {}).get("code")
                    if "designatedRegion" in wine_batch and isinstance(wine_batch.get("designatedRegion"), dict) else None,
                "designatedVariety_id": wine_batch.get("designatedVariety", {}).get("id")
                    if "designatedVariety" in wine_batch and isinstance(wine_batch.get("designatedVariety"), dict) else None,
                "designatedVariety_name": wine_batch.get("designatedVariety", {}).get("name")
                    if "designatedVariety" in wine_batch and isinstance(wine_batch.get("designatedVariety"), dict) else None,
                "designatedVariety_code": wine_batch.get("designatedVariety", {}).get("code")
                    if "designatedVariety" in wine_batch and isinstance(wine_batch.get("designatedVariety"), dict) else None,
                "productCategory_id": wine_batch.get("productCategory", {}).get("id")
                    if "productCategory" in wine_batch and isinstance(wine_batch.get("productCategory"), dict) else None,
                "productCategory_name": wine_batch.get("productCategory", {}).get("name")
                    if "productCategory" in wine_batch and isinstance(wine_batch.get("productCategory"), dict) else None,
                "productCategory_code": wine_batch.get("productCategory", {}).get("code")
                    if "productCategory" in wine_batch and isinstance(wine_batch.get("productCategory"), dict) else None,
                "designatedProduct_id": wine_batch.get("designatedProduct", {}).get("id")
                    if "designatedProduct" in wine_batch and isinstance(wine_batch.get("designatedProduct"), dict) else None,
                "designatedProduct_name": wine_batch.get("designatedProduct", {}).get("name")
                    if "designatedProduct" in wine_batch and isinstance(wine_batch.get("designatedProduct"), dict) else None,
                "designatedProduct_code": wine_batch.get("designatedProduct", {}).get("code")
                    if "designatedProduct" in wine_batch and isinstance(wine_batch.get("designatedProduct"), dict) else None,
                "grading_scaleId": wine_batch.get("grading", {}).get("scaleId")
                    if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
                "grading_scaleName": wine_batch.get("grading", {}).get("scaleName")
                    if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
                "grading_valueId": wine_batch.get("grading", {}).get("valueId")
                    if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
                "grading_valueName": wine_batch.get("grading", {}).get("valueName")
                    if "grading" in wine_batch and isinstance(wine_batch.get("grading"), dict) else None,
            }
            # Add cost fields
            cost = wine_detail.get("cost", {})
            for field in ["total", "fruit", "overhead", "storage", "additive", "bulk", "packaging", "operation", "freight", "other", "average"]:
                wine_batch_row[f"cost_{field}"] = cost.get(field)
            wine_batch_table.append(wine_batch_row)

        # --- Composition Table ---
        compositions = wine_detail.get("composition", [])
        vol_value = wine_detail.get("volume", {}).get("value")
        for composition in compositions:
            composition_id = generate_uid()
            perc = composition.get("percentage")
            comp_gal = None
            if vol_value is not None and perc is not None:
                try:
                    comp_gal = float(vol_value) * (float(perc) / 100.0)
                except Exception:
                    comp_gal = None  # fallback if conversion fails

            composition_row = {
                "composition_id": composition_id,
                "wine_details_id": wine_details_id,
                "percentage": composition.get("percentage"),
                "vintage": composition.get("vintage"),
                "subRegion": composition.get("subRegion"),
                "block_id": composition.get("block", {}).get("id")
                    if "block" in composition and isinstance(composition.get("block"), dict) else None,
                "block_name": composition.get("block", {}).get("name")
                    if "block" in composition and isinstance(composition.get("block"), dict) else None,
                "block_extId": composition.get("block", {}).get("extId")
                    if "block" in composition and isinstance(composition.get("block"), dict) else None,
                "region_id": composition.get("region", {}).get("id")
                    if "region" in composition and isinstance(composition.get("region"), dict) else None,
                "region_name": composition.get("region", {}).get("name")
                    if "region" in composition and isinstance(composition.get("region"), dict) else None,
                "variety_id": composition.get("variety", {}).get("id")
                    if "variety" in composition and isinstance(composition.get("variety"), dict) else None,
                "variety_name": composition.get("variety", {}).get("name")
                    if "variety" in composition and isinstance(composition.get("variety"), dict) else None,
                "CompGal": comp_gal,
            }
            composition_table.append(composition_row)

# --- Write to JSON files ---
with open(os.path.join(OUT_DIR, "shipments.json"), "w", encoding="utf-8") as f:
    json.dump(shipments_table, f, indent=2)

with open(os.path.join(OUT_DIR, "shipments_wine_details.json"), "w", encoding="utf-8") as f:
    json.dump(wine_details_table, f, indent=2)

with open(os.path.join(OUT_DIR, "shipments_wine_batch.json"), "w", encoding="utf-8") as f:
    json.dump(wine_batch_table, f, indent=2)

with open(os.path.join(OUT_DIR, "shipments_composition.json"), "w", encoding="utf-8") as f:
    json.dump(composition_table, f, indent=2)

print("Split complete! JSON tables written to", OUT_DIR)