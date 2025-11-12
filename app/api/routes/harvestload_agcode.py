# vintrick-backend/app/api/routes/harvestload_agcode.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.harvestload_agcode import HarvestLoadAgcode
from typing import List
from datetime import datetime, timezone

router = APIRouter()

def flatten_bulk_json(payload: list):
    rows = []
    for block in payload:
        season_year = block.get("SeasonYear")
        block_short_name = block.get("BlockShortName")
        for st in block.get("st", []):
            load_status = st.get("LoadStatus")
            for l in st.get("l", []):
                load_rec_date = l.get("LoadRecDate")
                weight_cert_id = l.get("WeightCertID")
                delivery_ticket = l.get("DeliveryTicket")
                inbound_container_count = l.get("Inbound Container Count")
                outbound_container_count = l.get("Outbound Container Count")
                harvest_date = l.get("HarvestDate")
                for v in l.get("v", []):
                    truck = v.get("Truck")
                    for t1 in v.get("t1", []):
                        trailer_01 = t1.get("Trailer 01")
                        for t2 in t1.get("t2", []):
                            trailer_02 = t2.get("Trailer 02")
                            for ci in t2.get("ci", []):
                                inbound_container_type = ci.get("Inbound Container Type")
                                for co in ci.get("co", []):
                                    outbound_container_type = co.get("Outbound Container Type")
                                    for pl in co.get("pl", []):
                                        deliver_to = pl.get("Deliver To")
                                        for iu in pl.get("iu", []):
                                            intended_use = iu.get("Intended Use")
                                            for ac in iu.get("ac", []):
                                                row = {
                                                    "season_year": season_year,
                                                    "block_short_name": block_short_name,
                                                    "load_status": load_status,
                                                    "load_rec_date": load_rec_date,
                                                    "weight_cert_id": weight_cert_id,
                                                    "delivery_ticket": delivery_ticket,
                                                    "inbound_container_count": inbound_container_count,
                                                    "outbound_container_count": outbound_container_count,
                                                    "harvest_date": harvest_date,
                                                    "truck": truck,
                                                    "trailer_01": trailer_01,
                                                    "trailer_02": trailer_02,
                                                    "inbound_container_type": inbound_container_type,
                                                    "outbound_container_type": outbound_container_type,
                                                    "deliver_to": deliver_to,
                                                    "intended_use": intended_use,
                                                    "harvest_type": ac.get("Harvest Type"),
                                                    "scale_operator": ac.get("Scale Operator"),
                                                    "gross_weight_value": ac.get("GrossWeight_Value"),
                                                    "gross_weight_unit": ac.get("GrossWeight_Unit"),
                                                    "tare_weight_value": ac.get("TareWeight_Value"),
                                                    "tare_weight_unit": ac.get("TareWeight_Unit"),
                                                    "net_weight_value": ac.get("NetWeight_Value"),
                                                    "net_weight_unit": ac.get("NetWeight_Unit"),
                                                    "last_modified": datetime.now(timezone.utc),
                                                    "synced": False,
                                                }
                                                rows.append(row)
    return rows

@router.post("/harvestload_agcode_bulk")
def upload_harvestload_agcode_bulk(payload: List[dict], db: Session = Depends(get_db)):
    try:
        flat_rows = flatten_bulk_json(payload)
        inserted = 0
        for row in flat_rows:
            db_obj = HarvestLoadAgcode(**row)
            db.add(db_obj)
            inserted += 1
        db.commit()
        return {"inserted": inserted, "ok": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))