# python tools/upload_vessels.py

import json
import os

from utils.helpers import safe_get_path, safe_get

JSON_PATH = os.getenv("VESSELS_JSON", "Main/data/GET--vessels/vessels.json")
OUT_DIR = os.getenv("VESSELS_SPLIT_DIR", "Main/data/GET--vessels/tables")
ID_OUT_DIR = "Main/data/id_tables"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ID_OUT_DIR, exist_ok=True)

def get_unspecified_block_name(variety_name):
    if variety_name and isinstance(variety_name, str) and variety_name.strip():
        code = variety_name.upper()[:3]
        return f"unspecified-{code}"
    return "unspecified-UNK"

vs_vessels_table = []
vs_wine_batch_table = []
vs_composition_table = []
vs_cost_table = []
vs_ttb_details_table = []

# ID tables for linking
vs_winery_table = {}
vs_productState_table = {}
vs_bond_table = {}
vs_taxClass_table = {}
vs_variety_table = {}
vs_region_table = {}
vs_block_table = {}
vs_subRegion_table = {}

with open(JSON_PATH, "r", encoding="utf-8") as f:
    vessels = json.load(f)

for vessel in vessels:
    vs_id = safe_get(vessel.get("id"))
    vs_winery_id = safe_get_path(vessel, ["winery", "id"])
    if vs_winery_id:
        vs_winery_table[vs_winery_id] = {
            "vs_winery_id": vs_winery_id,
            "vs_winery_name": safe_get_path(vessel, ["winery", "name"])
        }
    vs_productState_id = safe_get_path(vessel, ["productState", "id"])
    if vs_productState_id:
        vs_productState_table[vs_productState_id] = {
            "vs_productState_id": vs_productState_id,
            "vs_productState_name": safe_get_path(vessel, ["productState", "name"])
        }
    vs_bond_id = safe_get_path(vessel, ["ttbDetails", "bond", "id"])
    if vs_bond_id:
        vs_bond_table[vs_bond_id] = {
            "bond_id": vs_bond_id,
            "bond_name": safe_get_path(vessel, ["ttbDetails", "bond", "name"])
        }
    vs_taxClass_id = safe_get_path(vessel, ["ttbDetails", "taxClass", "id"])
    if vs_taxClass_id:
        vs_taxClass_table[vs_taxClass_id] = {
            "vs_taxClass_id": vs_taxClass_id,
            "vs_taxClass_name": safe_get_path(vessel, ["ttbDetails", "taxClass", "name"]),
            "vs_taxClass_federalName": safe_get_path(vessel, ["ttbDetails", "taxClass", "federalName"]),
        }
    # --- Vessels Table ---
    vessel_row = {
        "vs_id": vs_id,
        "vs_name": safe_get(vessel.get("name")),
        "vs_description": safe_get(vessel.get("description")),
        "vs_vesselType": safe_get(vessel.get("vesselType")),
        "vs_detailsAsAt": safe_get(vessel.get("detailsAsAt")),
        "vs_winery_id": vs_winery_id,
        "vs_productState_id": vs_productState_id,
        "vs_productState_expectedLossesPercentage": safe_get_path(vessel, ["productState", "expectedLossesPercentage"]),
        "vs_volume_unit": safe_get_path(vessel, ["volume", "unit"]),
        "vs_volume_value": safe_get_path(vessel, ["volume", "value"]),
        "vs_capacity_unit": safe_get_path(vessel, ["capacity", "unit"]),
        "vs_capacity_value": safe_get_path(vessel, ["capacity", "value"]),
        "vs_ullage_unit": safe_get_path(vessel, ["ullage", "unit"]),
        "vs_ullage_value": safe_get_path(vessel, ["ullage", "value"]),
        "vs_ttbDetails_id": vs_bond_id,
        "vs_ttbDetails_taxState": safe_get_path(vessel, ["ttbDetails", "taxState"]),
        "vs_ttbDetails_taxClass_id": vs_taxClass_id,
        "vs_ttbDetails_alcoholPercentage": safe_get_path(vessel, ["ttbDetails", "alcoholPercentage"]),
    }
    vs_vessels_table.append(vessel_row)

    # --- Wine Batch Table ---
    wine_batch = safe_get(vessel.get("wineBatch"))
    if wine_batch:
        vs_batch_designatedVariety_id = safe_get_path(wine_batch, ["designatedVariety", "id"])
        if vs_batch_designatedVariety_id:
            vs_variety_table[vs_batch_designatedVariety_id] = {
                "vs_batch_designatedVariety_id": vs_batch_designatedVariety_id,
                "vs_batch_designatedVariety_name": safe_get_path(wine_batch, ["designatedVariety", "name"])
            }
        vs_batch_designatedRegion_id = safe_get_path(wine_batch, ["designatedRegion", "id"])
        vs_batch_designatedRegion_code = safe_get_path(wine_batch, ["designatedRegion", "code"])
        if vs_batch_designatedRegion_id:
            vs_region_table[vs_batch_designatedRegion_id] = {
                "vs_batch_designatedRegion_id": vs_batch_designatedRegion_id,
                "vs_batch_designatedRegion_name": safe_get_path(wine_batch, ["designatedRegion", "name"]),
                "vs_batch_designatedRegion_code": vs_batch_designatedRegion_code
            }
        wine_batch_row = {
            "vs_id": vs_id,
            "vs_batch_id": safe_get(wine_batch.get("id")),
            "vs_batch_name": safe_get(wine_batch.get("name")),
            "vs_batch_description": safe_get(wine_batch.get("description")),
            "vs_batch_vintage": safe_get(wine_batch.get("vintage")),
            "vs_batch_program": safe_get(wine_batch.get("program")),
            "vs_batch_grading": safe_get(wine_batch.get("grading")),
            "vs_batch_productCategory": safe_get(wine_batch.get("productCategory")),
            "vs_batch_designatedProduct": safe_get(wine_batch.get("designatedProduct")),
            "vs_batch_designatedVariety_id": vs_batch_designatedVariety_id,
            "vs_batch_designatedRegion_id": vs_batch_designatedRegion_id,
            "vs_batch_designatedRegion_code": vs_batch_designatedRegion_code,
            "vs_batch_designatedSubRegion": safe_get(wine_batch.get("designatedSubRegion")),
        }
        vs_wine_batch_table.append(wine_batch_row)

    # --- Cost Table ---
    cost = safe_get(vessel.get("cost"))
    if cost:
        cost_row = {
            "vs_id": vs_id,
            "vs_total": safe_get(cost.get("total")),
            "vs_fruit": safe_get(cost.get("fruit")),
            "vs_overhead": safe_get(cost.get("overhead")),
            "vs_storage": safe_get(cost.get("storage")),
            "vs_additive": safe_get(cost.get("additive")),
            "vs_bulk": safe_get(cost.get("bulk")),
            "vs_packaging": safe_get(cost.get("packaging")),
            "vs_operation": safe_get(cost.get("operation")),
            "vs_freight": safe_get(cost.get("freight")),
            "vs_other": safe_get(cost.get("other")),
        }
        vs_cost_table.append(cost_row)

    # --- TTB Details Table ---
    ttb = safe_get(vessel.get("ttbDetails"))
    if ttb:
        bond_id = safe_get_path(ttb, ["bond", "id"])
        if bond_id:
            vs_bond_table[bond_id] = {
                "bond_id": bond_id,
                "bond_name": safe_get_path(ttb, ["bond", "name"])
            }
        taxClass_id = safe_get_path(ttb, ["taxClass", "id"])
        if taxClass_id:
            vs_taxClass_table[taxClass_id] = {
                "vs_taxClass_id": taxClass_id,
                "vs_taxClass_name": safe_get_path(ttb, ["taxClass", "name"]),
                "vs_taxClass_federalName": safe_get_path(ttb, ["taxClass", "federalName"]),
            }
        ttb_row = {
            "vs_id": vs_id,
            "vs_bond_id": bond_id,
            "vs_taxState": safe_get(ttb.get("taxState")),
            "vs_taxClass_id": taxClass_id,
            "vs_alcoholPercentage": safe_get(ttb.get("alcoholPercentage")),
        }
        vs_ttb_details_table.append(ttb_row)

    # --- Composition Table ---
    compositions = safe_get(vessel.get("composition")) or []
    vessel_volume_value = safe_get_path(vessel, ["volume", "value"])
    for composition in compositions:
        perc = safe_get(composition.get("percentage"))
        vs_CompGal = None
        if vessel_volume_value is not None and perc is not None:
            try:
                vs_CompGal = float(vessel_volume_value) * float(perc)
            except Exception:
                vs_CompGal = None
        block_id = safe_get_path(composition, ["block", "id"])
        block_name = safe_get_path(composition, ["block", "name"])
        variety_id = safe_get_path(composition, ["variety", "id"])
        variety_name = safe_get_path(composition, ["variety", "name"])
        region_id = safe_get_path(composition, ["region", "id"])
        region_name = safe_get_path(composition, ["region", "name"])
        subRegion_id = safe_get_path(composition, ["subRegion", "id"])
        subRegion_name = safe_get_path(composition, ["subRegion", "name"])
        if not block_name or block_name in ["", None]:
            block_name = get_unspecified_block_name(variety_name)
        if block_id:
            vs_block_table[block_id] = {
                "vs_block_id": block_id,
                "vs_block_name": block_name,
                "vs_block_extId": safe_get_path(composition, ["block", "extId"])
            }
        if region_id:
            vs_region_table[region_id] = {
                "vs_region_id": region_id,
                "vs_region_name": region_name,
                "vs_region_code": safe_get_path(composition, ["region", "code"])
            }
        if variety_id:
            vs_variety_table[variety_id] = {
                "vs_variety_id": variety_id,
                "vs_variety_name": variety_name,
                "vs_variety_code": safe_get_path(composition, ["variety", "code"])
            }
        if subRegion_id:
            vs_subRegion_table[subRegion_id] = {
                "vs_subRegion_id": subRegion_id,
                "vs_subRegion_name": subRegion_name,
                "vs_subRegion_code": safe_get_path(composition, ["subRegion", "code"])
            }
        composition_row = {
            "vs_id": vs_id,
            "vs_weighting": safe_get(composition.get("weighting")),
            "vs_percentage": perc,
            "vs_componentVolume_unit": safe_get_path(composition, ["componentVolume", "unit"]),
            "vs_componentVolume_value": safe_get_path(composition, ["componentVolume", "value"]),
            "vs_vintage": safe_get(composition.get("vintage")),
            "vs_block_id": block_id,
            "vs_region_id": region_id,
            "vs_variety_id": variety_id,
            "vs_subRegion_id": subRegion_id,
            "vs_CompGal": vs_CompGal,
        }
        vs_composition_table.append(composition_row)

# --- Write to JSON files (table outputs) ---
with open(os.path.join(OUT_DIR, "vs_vessels.json"), "w", encoding="utf-8") as f:
    json.dump(vs_vessels_table, f, indent=2)
with open(os.path.join(OUT_DIR, "vs_wine_batch.json"), "w", encoding="utf-8") as f:
    json.dump(vs_wine_batch_table, f, indent=2)
with open(os.path.join(OUT_DIR, "vs_composition.json"), "w", encoding="utf-8") as f:
    json.dump(vs_composition_table, f, indent=2)
with open(os.path.join(OUT_DIR, "vs_cost.json"), "w", encoding="utf-8") as f:
    json.dump(vs_cost_table, f, indent=2)
with open(os.path.join(OUT_DIR, "vs_ttb_details.json"), "w", encoding="utf-8") as f:
    json.dump(vs_ttb_details_table, f, indent=2)

# --- Write to JSON files (ID tables for linking) ---
with open(os.path.join(ID_OUT_DIR, "vs_winery.json"), "w", encoding="utf-8") as f:
    json.dump(list(vs_winery_table.values()), f, indent=2)
with open(os.path.join(ID_OUT_DIR, "vs_productState.json"), "w", encoding="utf-8") as f:
    json.dump(list(vs_productState_table.values()), f, indent=2)
with open(os.path.join(ID_OUT_DIR, "vs_bond.json"), "w", encoding="utf-8") as f:
    json.dump(list(vs_bond_table.values()), f, indent=2)
with open(os.path.join(ID_OUT_DIR, "vs_taxClass.json"), "w", encoding="utf-8") as f:
    json.dump(list(vs_taxClass_table.values()), f, indent=2)
with open(os.path.join(ID_OUT_DIR, "vs_variety.json"), "w", encoding="utf-8") as f:
    json.dump(list(vs_variety_table.values()), f, indent=2)
with open(os.path.join(ID_OUT_DIR, "vs_region.json"), "w", encoding="utf-8") as f:
    json.dump(list(vs_region_table.values()), f, indent=2)
with open(os.path.join(ID_OUT_DIR, "vs_block.json"), "w", encoding="utf-8") as f:
    json.dump(list(vs_block_table.values()), f, indent=2)
with open(os.path.join(ID_OUT_DIR, "vs_subRegion.json"), "w", encoding="utf-8") as f:
    json.dump(list(vs_subRegion_table.values()), f, indent=2)

print("Split complete! JSON tables written to", OUT_DIR, "and", ID_OUT_DIR)