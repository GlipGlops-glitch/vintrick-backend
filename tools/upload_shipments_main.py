# python tools/upload_shipments_main.py

import json
import os

def safe_get(val):
    return val if val not in [None, "NULL"] else None

def safe_get_path(d, keys):
    """Safely get nested keys from a dict."""
    v = d
    for k in keys:
        if not isinstance(v, dict):
            return None
        v = v.get(k)
    return safe_get(v)

JSON_PATH = os.getenv("SHIPMENTS_JSON", "Main/data/GET--shipments/all_shipments.json")
OUT_DIR = os.getenv("SHIPMENTS_SPLIT_DIR", "Main/data/GET--shipments/tables")
ID_OUT_DIR = "Main/data/id_tables"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ID_OUT_DIR, exist_ok=True)

sh_shipments_table = []
sh_shipments_wine_details_table = []
sh_shipments_wine_batch_table = []
sh_shipments_composition_table = []
sh_shipments_inter_winery_table = []

# Lookup tables for child entities
sh_source_table = {}
sh_destination_table = {}
sh_loss_reason_table = {}
sh_designatedRegion_table = {}
sh_designatedVariety_table = {}
sh_productCategory_table = {}
sh_designatedProduct_table = {}
sh_grading_scale_table = {}
sh_grading_table = {}

with open(JSON_PATH, "r", encoding="utf-8") as f:
    shipments = json.load(f)
for shipment in shipments:
    shipment_id = safe_get(shipment.get("id"))
    reversed_val = safe_get(shipment.get("reversed"))
    dispatch_type_id = safe_get_path(shipment, ["dispatchType", "id"])
    type_val = safe_get(shipment.get("type"))
    # Only collect if not reversed (False or "False")
    if reversed_val in [True, "true", "True"]:
        continue

    # --- Deduplicate source table ---
    source_id = safe_get_path(shipment, ["source", "id"])
    if source_id:
        sh_source_table[source_id] = {
            "source_id": source_id,
            "source_name": safe_get_path(shipment, ["source", "name"]),
            "source_businessUnit": safe_get_path(shipment, ["source", "businessUnit"]),
        }

    # --- Deduplicate destination table ---
    destination_party_id = safe_get_path(shipment, ["destination", "party", "id"])
    destination_winery_name = safe_get_path(shipment, ["destination", "winery", "name"])
    if destination_party_id or destination_winery_name:
        sh_destination_table[destination_party_id or destination_winery_name] = {
            "destination_winery_name": destination_winery_name,
            "destination_party_id": destination_party_id,
            "destination_party_name": safe_get_path(shipment, ["destination", "party", "name"]),
        }

    # --- Shipments Table ---
    shipment_row = {
        "shipment_id": shipment_id,
        "workOrderNumber": safe_get(shipment.get("workOrderNumber")),
        "jobNumber": safe_get(shipment.get("jobNumber")),
        "shipmentNumber": safe_get(shipment.get("shipmentNumber")),
        "type": type_val,
        "occurredTime": safe_get(shipment.get("occurredTime")),
        "modifiedTime": safe_get(shipment.get("modifiedTime")),
        "reference": safe_get(shipment.get("reference")),
        "freightCode": safe_get(shipment.get("freightCode")),
        "reversed": reversed_val,
        "source_id": source_id,
        "destination_party_id": destination_party_id,
        "carrier": safe_get_path(shipment, ["carrier", "name"]) or safe_get(shipment.get("carrier")),
        "dispatchType_id": dispatch_type_id,
    }
    sh_shipments_table.append(shipment_row)

    # --- Inter Winery Table (type == INTER_WINERY) ---
    if type_val == "INTER_WINERY":
        inter_winery_row = {
            "shipment_id": shipment_id,
            "workOrderNumber": safe_get(shipment.get("workOrderNumber")),
            "jobNumber": safe_get(shipment.get("jobNumber")),
            "shipmentNumber": safe_get(shipment.get("shipmentNumber")),
            "occurredTime": safe_get(shipment.get("occurredTime")),
            "source_id": source_id,
            "destination_party_id": destination_party_id,
            "carrier": safe_get_path(shipment, ["carrier", "name"]) or safe_get(shipment.get("carrier")),
            "destination_winery_name": destination_winery_name,
        }
        sh_shipments_inter_winery_table.append(inter_winery_row)

    # --- Wine Details Table ---
    wine_details = shipment.get("wineDetails", [])
    for wine_detail in wine_details:
        wine_details_id = f"{shipment_id}:{safe_get(wine_detail.get('vessel'))}"
        loss_reason_id = safe_get_path(wine_detail, ["loss", "reason", "id"])
        if loss_reason_id:
            sh_loss_reason_table[loss_reason_id] = {
                "loss_reason_id": loss_reason_id,
                "loss_reason_name": safe_get_path(wine_detail, ["loss", "reason", "name"]),
            }
        wine_details_row = {
            "shipment_id": shipment_id,
            "wine_details_id": wine_details_id,
            "vessel": safe_get(wine_detail.get("vessel")),
            "batch": safe_get(wine_detail.get("batch")),
            "weight": safe_get(wine_detail.get("weight")),
            "volume_unit": safe_get_path(wine_detail, ["volume", "unit"]),
            "volume_value": safe_get_path(wine_detail, ["volume", "value"]),
            "loss_volume_unit": safe_get_path(wine_detail, ["loss", "volume", "unit"]),
            "loss_volume_value": safe_get_path(wine_detail, ["loss", "volume", "value"]),
            "loss_reason_id": loss_reason_id,
            "wineryBuilding_id": safe_get_path(wine_detail, ["wineryBuilding", "id"]),
        }
        sh_shipments_wine_details_table.append(wine_details_row)

        # --- Wine Batch Table ---
        wine_batch = safe_get(wine_detail.get("wineBatch"))
        if wine_batch:
            designatedRegion_id = safe_get_path(wine_batch, ["designatedRegion", "id"])
            if designatedRegion_id:
                sh_designatedRegion_table[designatedRegion_id] = {
                    "designatedRegion_id": designatedRegion_id,
                    "designatedRegion_name": safe_get_path(wine_batch, ["designatedRegion", "name"]),
                    "designatedRegion_code": safe_get_path(wine_batch, ["designatedRegion", "code"]),
                }
            designatedVariety_id = safe_get_path(wine_batch, ["designatedVariety", "id"])
            if designatedVariety_id:
                sh_designatedVariety_table[designatedVariety_id] = {
                    "designatedVariety_id": designatedVariety_id,
                    "designatedVariety_name": safe_get_path(wine_batch, ["designatedVariety", "name"]),
                    "designatedVariety_code": safe_get_path(wine_batch, ["designatedVariety", "code"]),
                }
            productCategory_id = safe_get_path(wine_batch, ["productCategory", "id"])
            if productCategory_id:
                sh_productCategory_table[productCategory_id] = {
                    "productCategory_id": productCategory_id,
                    "productCategory_name": safe_get_path(wine_batch, ["productCategory", "name"]),
                    "productCategory_code": safe_get_path(wine_batch, ["productCategory", "code"]),
                }
            designatedProduct_id = safe_get_path(wine_batch, ["designatedProduct", "id"])
            if designatedProduct_id:
                sh_designatedProduct_table[designatedProduct_id] = {
                    "designatedProduct_id": designatedProduct_id,
                    "designatedProduct_name": safe_get_path(wine_batch, ["designatedProduct", "name"]),
                    "designatedProduct_code": safe_get_path(wine_batch, ["designatedProduct", "code"]),
                }
            grading_scaleId = safe_get_path(wine_batch, ["grading", "scaleId"])
            if grading_scaleId:
                sh_grading_scale_table[grading_scaleId] = {
                    "grading_scaleId": grading_scaleId,
                    "grading_scaleName": safe_get_path(wine_batch, ["grading", "scaleName"]),
                }
            grading_valueId = safe_get_path(wine_batch, ["grading", "valueId"])
            if grading_valueId:
                sh_grading_table[grading_valueId] = {
                    "grading_valueId": grading_valueId,
                    "grading_valueName": safe_get_path(wine_batch, ["grading", "valueName"]),
                }

            wine_batch_row = {
                "shipment_id": shipment_id,
                "wine_details_id": wine_details_id,
                "id": safe_get(wine_batch.get("id")),
                "designatedRegion_id": designatedRegion_id,
                "designatedVariety_id": designatedVariety_id,
                "productCategory_id": productCategory_id,
                "designatedProduct_id": designatedProduct_id,
                "grading_scaleId": grading_scaleId,
                "grading_valueId": grading_valueId,
            }
            sh_shipments_wine_batch_table.append(wine_batch_row)

        # --- Composition Table ---
        compositions = wine_detail.get("composition", [])
        vol_value = safe_get_path(wine_detail, ["volume", "value"])
        for composition in compositions:
            perc = safe_get(composition.get("percentage"))
            comp_gal = None
            if vol_value is not None and perc is not None:
                try:
                    comp_gal = float(vol_value) * (float(perc) / 100.0)
                except Exception:
                    comp_gal = None
            block_id = safe_get_path(composition, ["block", "id"])
            composition_row = {
                "shipment_id": shipment_id,
                "block_id": block_id,
                "vintage": safe_get(composition.get("vintage")),
                "percentage": perc,
                "CompGal": comp_gal,
            }
            sh_shipments_composition_table.append(composition_row)

# --- Write to JSON files ---
with open(os.path.join(OUT_DIR, "sh_shipments.json"), "w", encoding="utf-8") as f:
    json.dump(sh_shipments_table, f, indent=2)

with open(os.path.join(OUT_DIR, "sh_shipments_inter_winery.json"), "w", encoding="utf-8") as f:
    json.dump(sh_shipments_inter_winery_table, f, indent=2)

with open(os.path.join(OUT_DIR, "sh_shipments_wine_details.json"), "w", encoding="utf-8") as f:
    json.dump(sh_shipments_wine_details_table, f, indent=2)

with open(os.path.join(OUT_DIR, "sh_shipments_wine_batch.json"), "w", encoding="utf-8") as f:
    json.dump(sh_shipments_wine_batch_table, f, indent=2)

with open(os.path.join(OUT_DIR, "sh_shipments_composition.json"), "w", encoding="utf-8") as f:
    json.dump(sh_shipments_composition_table, f, indent=2)

# Write ID tables for linking
with open(os.path.join(ID_OUT_DIR, "sh_source.json"), "w", encoding="utf-8") as f:
    json.dump(list(sh_source_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "sh_destination.json"), "w", encoding="utf-8") as f:
    json.dump(list(sh_destination_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "sh_loss_reason.json"), "w", encoding="utf-8") as f:
    json.dump(list(sh_loss_reason_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "sh_designatedRegion.json"), "w", encoding="utf-8") as f:
    json.dump(list(sh_designatedRegion_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "sh_designatedVariety.json"), "w", encoding="utf-8") as f:
    json.dump(list(sh_designatedVariety_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "sh_productCategory.json"), "w", encoding="utf-8") as f:
    json.dump(list(sh_productCategory_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "sh_designatedProduct.json"), "w", encoding="utf-8") as f:
    json.dump(list(sh_designatedProduct_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "sh_grading_scale.json"), "w", encoding="utf-8") as f:
    json.dump(list(sh_grading_scale_table.values()), f, indent=2)

with open(os.path.join(ID_OUT_DIR, "sh_grading.json"), "w", encoding="utf-8") as f:
    json.dump(list(sh_grading_table.values()), f, indent=2)

print("Split complete! JSON tables written to", OUT_DIR, "and", ID_OUT_DIR)