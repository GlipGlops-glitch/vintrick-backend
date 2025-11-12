# vintrick-backend/tools/seed/harvestload_agcode_seed.py
# Script to generate 20 seed records for harvestload_agcode table

import uuid
import random
from datetime import datetime, timedelta, timezone
import json

BLOCKS = ["10CS74", "MACS8C", "12CS17", "12CS18", "AUCS19", "AUCH08", "CKCH42", "EPSY22", "EPSB27", "ZKSB9F", "IWCS24", "MCMV44", "KOSY14", "10SB04", "12CH01", "10CS67", "12CH47", "FMGT0A", "FMGT0B", "EGCH06"]
TRUCKS = ["SMWE", "901", "7892", "301", "9270", "38419RP", "83", "C47838K", "10444", "9186"]
TRAILERS = ["64139AA", "1790-ZU", "9340-ZS", "4781-ZU", "5", "0662-XV", "81765AB", "1789-ZU", "9238-YB", None]
CONTAINERS = ["Bin", "Tank", "Trailer", None]
DELIVER_TO = ["CC W", "CC R", "Canoe", None]
INTENDED_USE = ["CSM", "FTH", "COL", None]
HARVEST_TYPE = ["Machine Harvest", "Hand Harvest", None]
SCALE_OPS = ["Alcantar, Adriana", "Moreno, Samantha", "Borrego, Kasandra", "Alberto Carrasco", None]

def random_date(start, end):
    """Return a random datetime between two datetimes."""
    return start + timedelta(seconds=random.randint(0, int((end-start).total_seconds())))

seed_data = []
start_date = datetime(2024, 9, 1, tzinfo=timezone.utc)
end_date = datetime(2024, 10, 31, tzinfo=timezone.utc)

for i in range(20):
    block = BLOCKS[i % len(BLOCKS)]
    truck = random.choice(TRUCKS)
    trailer_01 = random.choice(TRAILERS)
    trailer_02 = random.choice(TRAILERS)
    inbound_type = random.choice(CONTAINERS)
    outbound_type = random.choice(CONTAINERS)
    deliver_to = random.choice(DELIVER_TO)
    intended_use = random.choice(INTENDED_USE)
    harvest_type = random.choice(HARVEST_TYPE)
    scale_operator = random.choice(SCALE_OPS)

    dt = random_date(start_date, end_date)
    load_rec_date = dt.isoformat()
    harvest_date = (dt - timedelta(days=1)).date().isoformat()
    last_modified = datetime.now(timezone.utc).isoformat()

    rec = {
        "season_year": str(2024 + (i % 2)),
        "block_short_name": block,
        "load_status": random.choice(["Daily", "Complete", "Pending"]),
        "load_rec_date": load_rec_date,
        "weight_cert_id": str(10000 + i),
        "delivery_ticket": f"{random.randint(200000,299999)}",
        "inbound_container_count": random.randint(1, 20),
        "outbound_container_count": random.randint(1, 20),
        "harvest_date": harvest_date,
        "truck": truck,
        "trailer_01": trailer_01,
        "trailer_02": trailer_02,
        "inbound_container_type": inbound_type,
        "outbound_container_type": outbound_type,
        "deliver_to": deliver_to,
        "intended_use": intended_use,
        "harvest_type": harvest_type,
        "scale_operator": scale_operator,
        "gross_weight_value": round(random.uniform(10000, 100000), 2),
        "gross_weight_unit": "tn",
        "tare_weight_value": round(random.uniform(5000, 80000), 2),
        "tare_weight_unit": "tn",
        "net_weight_value": round(random.uniform(2000, 80000), 2),
        "net_weight_unit": "tn",
        "last_modified": last_modified,
        "synced": False,
    }
    seed_data.append(rec)

# Write to JSON file for bulk testing, or print for cURL/Postman
with open("vintrick-backend/tools/seed/harvestload_agcode_seed.json", "w") as f:
    json.dump(seed_data, f, indent=2)

print("Seed data written to vintrick-backend/tools/seed/harvestload_agcode_seed.json")