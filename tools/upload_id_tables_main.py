# python tools/upload_id_tables_main.py

import json
import os

ID_DIR = "Main/data/id_tables"
OUT_DIR = "Main/data/id_tables/consolidated"
os.makedirs(OUT_DIR, exist_ok=True)

# ---- Consolidate BLOCKS ----
block_files = [
    "fr_blocks.json", "in_block.json", "vs_block.json", "bl_blocks.json"
]
main_blocks = {}
for fname in block_files:
    path = os.path.join(ID_DIR, fname)
    if not os.path.isfile(path):
        print(f"Block file not found: {fname}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            block_id = (
                row.get("fr_block_id") or 
                row.get("in_block_id") or 
                row.get("vs_block_id") or
                row.get("bl_block_id")
            )
            if not block_id:
                continue
            block_name = (
                row.get("fr_block_name") or 
                row.get("in_block_name") or 
                row.get("vs_block_name") or
                row.get("bl_block_name")
            )
            block_extId = (
                row.get("fr_block_externalCode") or
                row.get("in_block_extId") or
                row.get("vs_block_extId") or
                row.get("bl_block_extId")
            )
            # Merge/Fill missing if duplicate block_id
            if block_id in main_blocks:
                if not main_blocks[block_id]["main_block_name"] and block_name:
                    main_blocks[block_id]["main_block_name"] = block_name
                if not main_blocks[block_id]["main_block_extId"] and block_extId:
                    main_blocks[block_id]["main_block_extId"] = block_extId
            else:
                main_blocks[block_id] = {
                    "main_block_id": block_id,
                    "main_block_name": block_name,
                    "main_block_extId": block_extId
                }
with open(os.path.join(OUT_DIR, "main_blocks.json"), "w", encoding="utf-8") as f:
    json.dump(list(main_blocks.values()), f, indent=2)

# ---- Consolidate VARIETIES ----
variety_files = [
    "fr_varieties.json", "in_variety.json", "sh_designatedVariety.json", "vs_variety.json", "bl_variety.json"
]
main_varieties = {}
for fname in variety_files:
    path = os.path.join(ID_DIR, fname)
    if not os.path.isfile(path):
        print(f"Variety file not found: {fname}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            variety_id = (
                row.get("fr_variety_id") or
                row.get("in_variety_id") or
                row.get("sh_designatedVariety_id") or
                row.get("vs_variety_id") or
                row.get("vs_batch_designatedVariety_id") or
                row.get("bl_variety_id")
            )
            if not variety_id:
                continue
            variety_name = (
                row.get("fr_variety_name") or
                row.get("in_variety_name") or
                row.get("sh_designatedVariety_name") or
                row.get("vs_variety_name") or
                row.get("vs_batch_designatedVariety_name") or
                row.get("bl_variety_name")
            )
            variety_code = (
                row.get("fr_variety_shortCode") or
                row.get("in_variety_code") or
                row.get("sh_designatedVariety_code") or
                row.get("vs_variety_code") or
                row.get("vs_batch_designatedVariety_code")
            )
            if variety_id in main_varieties:
                if not main_varieties[variety_id]["main_variety_name"] and variety_name:
                    main_varieties[variety_id]["main_variety_name"] = variety_name
                if not main_varieties[variety_id]["main_variety_code"] and variety_code:
                    main_varieties[variety_id]["main_variety_code"] = variety_code
            else:
                main_varieties[variety_id] = {
                    "main_variety_id": variety_id,
                    "main_variety_name": variety_name,
                    "main_variety_code": variety_code
                }
with open(os.path.join(OUT_DIR, "main_varieties.json"), "w", encoding="utf-8") as f:
    json.dump(list(main_varieties.values()), f, indent=2)

# ---- Consolidate WINERIES ----
winery_files = [
    "fr_wineries.json", "vs_winery.json", "sh_source.json"
]
main_wineries = {}

for fname in winery_files:
    path = os.path.join(ID_DIR, fname)
    if not os.path.isfile(path):
        print(f"Winery file not found: {fname}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            # Try all possible id fields
            winery_id = (
                row.get("fr_winery_id") or
                row.get("vs_winery_id") or
                row.get("source_id")
            )
            if not winery_id:
                continue
            # Try all possible name fields
            winery_name = (
                row.get("fr_winery_name") or
                row.get("vs_winery_name") or
                row.get("source_name")
            )
            # Try business unit field if available
            winery_business_unit = (
                row.get("source_businessUnit") or
                row.get("fr_winery_businessUnit") or
                row.get("vs_winery_businessUnit")
            )
            if winery_id in main_wineries:
                if not main_wineries[winery_id]["main_winery_name"] and winery_name:
                    main_wineries[winery_id]["main_winery_name"] = winery_name
                # Only set business unit if not present and available
                if not main_wineries[winery_id].get("main_winery_businessUnit") and winery_business_unit:
                    main_wineries[winery_id]["main_winery_businessUnit"] = winery_business_unit
            else:
                main_wineries[winery_id] = {
                    "main_winery_id": winery_id,
                    "main_winery_name": winery_name,
                }
                if winery_business_unit:
                    main_wineries[winery_id]["main_winery_businessUnit"] = winery_business_unit

with open(os.path.join(OUT_DIR, "main_wineries.json"), "w", encoding="utf-8") as f:
    json.dump(list(main_wineries.values()), f, indent=2)

# ---- Consolidate GROWERS ----
grower_files = [
    "bl_grower.json"
]
main_growers = {}
for fname in grower_files:
    path = os.path.join(ID_DIR, fname)
    if not os.path.isfile(path):
        print(f"Grower file not found: {fname}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            grower_id = row.get("bl_grower_id")
            if not grower_id:
                continue
            grower_name = row.get("bl_grower_name")
            grower_extId = row.get("bl_grower_extId")
            if grower_id in main_growers:
                if not main_growers[grower_id]["main_grower_name"] and grower_name:
                    main_growers[grower_id]["main_grower_name"] = grower_name
                if not main_growers[grower_id]["main_grower_extId"] and grower_extId:
                    main_growers[grower_id]["main_grower_extId"] = grower_extId
            else:
                main_growers[grower_id] = {
                    "main_grower_id": grower_id,
                    "main_grower_name": grower_name,
                    "main_grower_extId": grower_extId
                }
with open(os.path.join(OUT_DIR, "main_growers.json"), "w", encoding="utf-8") as f:
    json.dump(list(main_growers.values()), f, indent=2)

# ---- Consolidate VINEYARDS ----
vineyard_files = [
    "bl_vineyard.json"
]
main_vineyards = {}
for fname in vineyard_files:
    path = os.path.join(ID_DIR, fname)
    if not os.path.isfile(path):
        print(f"Vineyard file not found: {fname}")
        continue
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            vineyard_id = row.get("bl_vineyard_id")
            if not vineyard_id:
                continue
            vineyard_name = row.get("bl_vineyard_name")
            vineyard_grower_id = row.get("bl_vineyard_grower_id")
            vineyard_grower_name = row.get("bl_vineyard_grower_name")
            vineyard_grower_extId = row.get("bl_vineyard_grower_extId")
            if vineyard_id in main_vineyards:
                if not main_vineyards[vineyard_id]["main_vineyard_name"] and vineyard_name:
                    main_vineyards[vineyard_id]["main_vineyard_name"] = vineyard_name
                if not main_vineyards[vineyard_id]["main_vineyard_grower_id"] and vineyard_grower_id:
                    main_vineyards[vineyard_id]["main_vineyard_grower_id"] = vineyard_grower_id
                if not main_vineyards[vineyard_id]["main_vineyard_grower_name"] and vineyard_grower_name:
                    main_vineyards[vineyard_id]["main_vineyard_grower_name"] = vineyard_grower_name
                if not main_vineyards[vineyard_id]["main_vineyard_grower_extId"] and vineyard_grower_extId:
                    main_vineyards[vineyard_id]["main_vineyard_grower_extId"] = vineyard_grower_extId
            else:
                main_vineyards[vineyard_id] = {
                    "main_vineyard_id": vineyard_id,
                    "main_vineyard_name": vineyard_name,
                    "main_vineyard_grower_id": vineyard_grower_id,
                    "main_vineyard_grower_name": vineyard_grower_name,
                    "main_vineyard_grower_extId": vineyard_grower_extId
                }
with open(os.path.join(OUT_DIR, "main_vineyards.json"), "w", encoding="utf-8") as f:
    json.dump(list(main_vineyards.values()), f, indent=2)

# ---- Consolidate REGIONS ----
region_files = [
    "fr_regions.json", "vs_region.json", "in_region.json", "bl_region.json"
]
def consolidate_table(table_name, files, id_keys, name_keys=None, code_keys=None):
    main_table = {}
    for fname in files:
        path = os.path.join(ID_DIR, fname)
        if not os.path.isfile(path):
            print(f"{table_name} file not found: {fname}")
            continue
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for row in data:
                the_id = None
                for k in id_keys:
                    if row.get(k):
                        the_id = row[k]
                        break
                if not the_id:
                    continue
                the_name = None
                if name_keys:
                    for k in name_keys:
                        if row.get(k):
                            the_name = row[k]
                            break
                the_code = None
                if code_keys:
                    for k in code_keys:
                        if row.get(k):
                            the_code = row[k]
                            break
                if the_id in main_table:
                    if name_keys and not main_table[the_id][f"{table_name}_name"] and the_name:
                        main_table[the_id][f"{table_name}_name"] = the_name
                    if code_keys and not main_table[the_id][f"{table_name}_code"] and the_code:
                        main_table[the_id][f"{table_name}_code"] = the_code
                else:
                    new_row = {f"{table_name}_id": the_id}
                    if name_keys: new_row[f"{table_name}_name"] = the_name
                    if code_keys: new_row[f"{table_name}_code"] = the_code
                    main_table[the_id] = new_row
    with open(os.path.join(OUT_DIR, f"{table_name}.json"), "w", encoding="utf-8") as f:
        json.dump(list(main_table.values()), f, indent=2)

consolidate_table(
    "main_regions",
    region_files,
    ["fr_region_id", "vs_region_id", "in_region_id", "bl_region_id"],
    ["fr_region_name", "vs_region_name", "in_region_name", "bl_region_name"],
    ["fr_region_shortCode", "vs_region_code", "in_region_code"]
)

# ---- Consolidate SUBREGIONS ----
subregion_files = [
    "vs_subRegion.json", "in_subRegion.json", "bl_subregion.json"
]
consolidate_table(
    "main_subRegions",
    subregion_files,
    ["vs_subRegion_id", "in_subRegion_id", "bl_subRegion_id"],
    ["vs_subRegion_name", "in_subRegion_name", "bl_subRegion_name"],
    ["vs_subRegion_code", "in_subRegion_code", "bl_subRegion_code"]
)

print("Consolidation complete! See:", OUT_DIR)