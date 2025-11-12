# After both special_transfer_table and special_transfer_from_intransit_table are populated

special_transfer_link_table = []

# Build index for fast lookup on from_intransit
from_intransit_index = {}
for idx, row in enumerate(special_transfer_from_intransit_table):
    key = (row.get("from_ts_name"), row.get("from_ts_volOut"))
    from_intransit_index.setdefault(key, []).append((idx, row))

# Now, scan the "to" in special_transfer_table and match against "from" in special_transfer_from_intransit_table
for idx_to, to_row in enumerate(special_transfer_table):
    key = (to_row.get("to_ts_name"), to_row.get("to_ts_volIn"))
    matches = from_intransit_index.get(key, [])
    for idx_from, from_row in matches:
        # Build the link (you can add more fields if you want)
        link_row = {
            "special_transfer_table_idx": idx_to,
            "special_transfer_table_subOperationId": to_row.get("ts_subOperationId"),
            "special_transfer_from_intransit_table_idx": idx_from,
            "special_transfer_from_intransit_table_subOperationId": from_row.get("ts_subOperationId"),
            "vessel_name": key[0],
            "volume": key[1]
        }
        special_transfer_link_table.append(link_row)

# Write output
with open(os.path.join(OUT_DIR, "special_transfer_link_table.json"), "w", encoding="utf-8") as f:
    safe_json_dump(special_transfer_link_table, f)