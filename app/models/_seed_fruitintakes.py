# vintrick-backend/app/models/_seed_fruitintakes.py
# Example seed data for the `fruitintakes` table.
# Run this as a script using your SQLAlchemy session setup.

import uuid
from datetime import datetime, timezone
from app.models.fruitintake import FruitIntake
from app.core.db import SessionLocal

seed_data = [
    {
        "uid": str(uuid.uuid4()),
        "block_extid": "U01234",
        "block_name": "CH1",
        "vintage": 2022,
        "bookingNumber": "B9288",
        "owner_extid": "O66253",
        "owner_name": "CBI",
        "dateOccurred": 164876283628,
        "timeOut": 164876283628,
        "timeIn": 164876293628,
        "weighTag": "PH-OB-50228768760",
        "externalWeighTag": "PH-OB-50228768760",
        "winery_bu": "US57",
        "winery_name": "My Winery",
        "scale_name": "TRUCK SCALES",
        "gross_value": 7.54,
        "gross_unit": "tn",
        "tare_value": 2.5,
        "tare_unit": "tn",
        "net_value": 5.04,
        "net_unit": "tn",
        "jobStatus": "complete",
        "intendedProduct_name": "CHCH21",
        "unitPrice_value": 1200,
        "unitPrice_unit": "$ / ton",
        "metrics": [
            {"name": "Brix", "value": 23},
            {"name": "MOG", "value": 2},
            {"name": "NIRS", "value": 54},
            {"name": "pH", "value": 3.4},
            {"name": "Temp", "value": 65},
            {"name": "VA", "value": 2.9},
        ],
        "harvestMethod": "machine",
        "weighMasterText": "Deputy John Smith",
        "carrier_name": "Acme Trucking",
        "carrier_extid": "C7363",
        "consignmentNote": "TH78352",
        "driverName": "Adam Sapple",
        "lastLoad": True,
        "operatorNotes": "My operator notes",
        "truckRegistration": "ABC-123",
        "linkEarliestBooking": False,
        "last_modified": datetime.now(timezone.utc),
        "synced": False
    },
    {
        "uid": str(uuid.uuid4()),
        "block_extid": "U05678",
        "block_name": "CH2",
        "vintage": 2023,
        "bookingNumber": "B9289",
        "owner_extid": "O66254",
        "owner_name": "Winery XYZ",
        "dateOccurred": 165876283628,
        "timeOut": 165876283628,
        "timeIn": 165876293628,
        "weighTag": "PH-OB-50228768888",
        "externalWeighTag": "PH-OB-50228768888",
        "winery_bu": "US58",
        "winery_name": "Another Winery",
        "scale_name": "BIN SCALES",
        "gross_value": 5.00,
        "gross_unit": "tn",
        "tare_value": 1.25,
        "tare_unit": "tn",
        "net_value": 3.75,
        "net_unit": "tn",
        "jobStatus": "complete",
        "intendedProduct_name": "MERL23",
        "unitPrice_value": 950,
        "unitPrice_unit": "$ / ton",
        "metrics": [
            {"name": "Brix", "value": 21},
            {"name": "MOG", "value": 3},
            {"name": "NIRS", "value": 49},
            {"name": "pH", "value": 3.3},
            {"name": "Temp", "value": 62},
            {"name": "VA", "value": 2.7},
        ],
        "harvestMethod": "hand",
        "weighMasterText": "Deputy Jane Doe",
        "carrier_name": "Fruit Movers",
        "carrier_extid": "C7364",
        "consignmentNote": "TH78353",
        "driverName": "Eve Apple",
        "lastLoad": False,
        "operatorNotes": "Good condition",
        "truckRegistration": "XYZ-789",
        "linkEarliestBooking": True,
        "last_modified": datetime.now(timezone.utc),
        "synced": False
    }
]

def seed_fruitintakes():
    db = SessionLocal()
    for row in seed_data:
        db_obj = FruitIntake(**row)
        db.add(db_obj)
    db.commit()
    db.close()
    print("Seed fruitintakes inserted.")

if __name__ == "__main__":
    seed_fruitintakes()