# vintrick-backend/app/models/_seed_harvestloads.py
# Example seed data for the `harvestloads` table.
# Run this as a script (or from a notebook/click CLI) using your SQLAlchemy session.

import uuid
from datetime import datetime, timezone
from app.models.harvestload import HarvestLoad
from app.core.db import SessionLocal

seed_data = [
    {
        "uid": str(uuid.uuid4()),
        "Vintrace_ST": "VT-1111",
        "Block": "Block A",
        "Tons": 2.50,
        "Press": "Press 1",
        "Tank": "Tank 3",
        "WO": "WO-2025-001",
        "Date_Received": "2025-07-25",
        "AgCode_ST": "AG001",
        "Time_Received": "08:30",
        "Wine_Type": "Chardonnay",
        "Est_Tons_1": 2.40,
        "Est_Tons_2": 2.45,
        "Est_Tons_3": 2.50,
        "Press_Pick_2": "Y",
        "Linked": "N",
        "Crush_Pad": "Pad A",
        "Status": "Received",
        "last_modified": datetime.now(timezone.utc),
        "synced": False
    },
    {
        "uid": str(uuid.uuid4()),
        "Vintrace_ST": "VT-2222",
        "Block": "Block B",
        "Tons": 3.10,
        "Press": "Press 2",
        "Tank": "Tank 4",
        "WO": "WO-2025-002",
        "Date_Received": "2025-07-26",
        "AgCode_ST": "AG002",
        "Time_Received": "09:15",
        "Wine_Type": "Cabernet",
        "Est_Tons_1": 3.05,
        "Est_Tons_2": 3.10,
        "Est_Tons_3": 3.15,
        "Press_Pick_2": "N",
        "Linked": "Y",
        "Crush_Pad": "Pad B",
        "Status": "Crushed",
        "last_modified": datetime.now(timezone.utc),
        "synced": False
    },
    {
        "uid": str(uuid.uuid4()),
        "Vintrace_ST": "VT-3333",
        "Block": "Block C",
        "Tons": 1.80,
        "Press": "Press 3",
        "Tank": "Tank 2",
        "WO": "WO-2025-003",
        "Date_Received": "2025-07-27",
        "AgCode_ST": "AG003",
        "Time_Received": "10:45",
        "Wine_Type": "Merlot",
        "Est_Tons_1": 1.75,
        "Est_Tons_2": 1.80,
        "Est_Tons_3": 1.85,
        "Press_Pick_2": "Y",
        "Linked": "Y",
        "Crush_Pad": "Pad C",
        "Status": "Awaiting",
        "last_modified": datetime.now(timezone.utc),
        "synced": False
    }
]

def seed_harvestloads():
    db = SessionLocal()
    for row in seed_data:
        db_obj = HarvestLoad(**row)
        db.add(db_obj)
    db.commit()
    db.close()
    print("Seed data inserted.")

if __name__ == "__main__":
    seed_harvestloads()