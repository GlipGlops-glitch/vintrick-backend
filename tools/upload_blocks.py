# python tools/upload_blocks.py

import json
import os

def safe_get(val):
    return val if val not in [None, "NULL"] else None

def safe_get_path(d, keys):
    """Safely get nested keys from a dict or None."""
    v = d
    for k in keys:
        if not isinstance(v, dict):
            return None
        v = v.get(k)
    return safe_get(v)

JSON_PATH = os.getenv("BLOCKS_JSON", "Main/data/GET--blocks/blocks.json")
ID_OUT_DIR = "Main/data/id_tables"
os.makedirs(ID_OUT_DIR, exist_ok=True)

bl_blocks_table = []
bl_grower_table = []
bl_vineyard_table = []
bl_region_table = []
bl_subregion_table = []
bl_variety_table = []

for_block_id = lambda block: safe_get(block.get("id"))

with open(JSON_PATH, "r", encoding="utf-8") as f:
    blocks = json.load(f)

for block in blocks:
    block_id = for_block_id(block)

    # --- Block Table ---
    block_row = {
        "bl_block_id": block_id,
        "bl_block_name": safe_get(block.get("name")),
        "bl_block_extId": safe_get(block.get("extId")),
        "bl_block_description": safe_get(block.get("description")),
        "bl_block_code": safe_get(block.get("code")),
        "bl_block_rowNumbers": safe_get(block.get("rowNumbers")),
        "bl_block_estate": safe_get(block.get("estate")),
        "bl_block_intendedUse": safe_get(block.get("intendedUse")),
        "bl_block_grading": safe_get(block.get("grading")),
        "bl_block_inactive": safe_get(block.get("inactive")),
        "bl_block_fruitPlacement": safe_get(block.get("fruitPlacement")),
        # foreign keys for lookup tables
        "bl_grower_id": safe_get_path(block, ["grower", "id"]),
        "bl_vineyard_id": safe_get_path(block, ["vineyard", "id"]),
        "bl_region_id": safe_get_path(block, ["region", "id"]),
        "bl_subRegion_id": safe_get_path(block, ["subRegion", "id"]),
        "bl_variety_id": safe_get_path(block, ["variety", "id"]),
    }
    bl_blocks_table.append(block_row)

    # --- Grower Table ---
    grower = block.get("grower")
    if grower:
        grower_row = {
            "bl_grower_id": safe_get(grower.get("id")),
            "bl_grower_name": safe_get(grower.get("name")),
            "bl_grower_extId": safe_get(grower.get("extId")),
        }
        bl_grower_table.append(grower_row)

    # --- Vineyard Table ---
    vineyard = block.get("vineyard")
    if vineyard:
        vineyard_row = {
            "bl_vineyard_id": safe_get(vineyard.get("id")),
            "bl_vineyard_name": safe_get(vineyard.get("name")),
            "bl_vineyard_grower_id": safe_get_path(vineyard, ["grower", "id"]),
            "bl_vineyard_grower_name": safe_get_path(vineyard, ["grower", "name"]),
            "bl_vineyard_grower_extId": safe_get_path(vineyard, ["grower", "extId"]),
        }
        bl_vineyard_table.append(vineyard_row)

    # --- Region Table ---
    region = block.get("region")
    if region:
        region_row = {
            "bl_region_id": safe_get(region.get("id")),
            "bl_region_name": safe_get(region.get("name")),
        }
        bl_region_table.append(region_row)

    # --- SubRegion Table ---
    subregion = block.get("subRegion")
    if subregion:
        subregion_row = {
            "bl_subRegion_id": safe_get(subregion.get("id")),
            "bl_subRegion_name": safe_get(subregion.get("name")),
        }
        bl_subregion_table.append(subregion_row)

    # --- Variety Table ---
    variety = block.get("variety")
    if variety:
        variety_row = {
            "bl_variety_id": safe_get(variety.get("id")),
            "bl_variety_name": safe_get(variety.get("name")),
        }
        bl_variety_table.append(variety_row)

# --- Deduplicate lookup tables ---
def deduplicate(table, key_field):
    seen = set()
    deduped = []
    for row in table:
        key = row[key_field]
        if key and key not in seen:
            seen.add(key)
            deduped.append(row)
    return deduped

bl_grower_table = deduplicate(bl_grower_table, "bl_grower_id")
bl_vineyard_table = deduplicate(bl_vineyard_table, "bl_vineyard_id")
bl_region_table = deduplicate(bl_region_table, "bl_region_id")
bl_subregion_table = deduplicate(bl_subregion_table, "bl_subRegion_id")
bl_variety_table = deduplicate(bl_variety_table, "bl_variety_id")

# --- Write to JSON files ---
with open(os.path.join(ID_OUT_DIR, "bl_blocks.json"), "w", encoding="utf-8") as f:
    json.dump(bl_blocks_table, f, indent=2)

with open(os.path.join(ID_OUT_DIR, "bl_grower.json"), "w", encoding="utf-8") as f:
    json.dump(bl_grower_table, f, indent=2)

with open(os.path.join(ID_OUT_DIR, "bl_vineyard.json"), "w", encoding="utf-8") as f:
    json.dump(bl_vineyard_table, f, indent=2)

with open(os.path.join(ID_OUT_DIR, "bl_region.json"), "w", encoding="utf-8") as f:
    json.dump(bl_region_table, f, indent=2)

with open(os.path.join(ID_OUT_DIR, "bl_subregion.json"), "w", encoding="utf-8") as f:
    json.dump(bl_subregion_table, f, indent=2)

with open(os.path.join(ID_OUT_DIR, "bl_variety.json"), "w", encoding="utf-8") as f:
    json.dump(bl_variety_table, f, indent=2)

print("Split complete! JSON tables written to", ID_OUT_DIR)