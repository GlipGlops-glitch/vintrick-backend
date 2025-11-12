# vintrick-backend/app/api/routes/shipments.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.shipment import ShipmentCreate, ShipmentOut
from app.crud.shipment import (
    create_shipment,
    get_shipment,
    get_shipment_by_number,
    get_all_shipments,
    update_shipment,
    delete_shipment
)
from app.api.deps import get_db
import subprocess  # <-- Required for upload endpoint

router = APIRouter()

@router.get("/shipments/", response_model=dict)
def list_shipments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, gt=0),
    db: Session = Depends(get_db)
):
    items, total = get_all_shipments(db, skip=skip, limit=limit)
    return {
        "items": [ShipmentOut.model_validate(item) for item in items],
        "total": total
    }

@router.post("/shipments/", response_model=ShipmentOut)
def create_shipment_route(
    shipment: ShipmentCreate, db: Session = Depends(get_db)
):
    # Check for duplicates by shipmentNumber
    if shipment.shipmentNumber:
        existing = get_shipment_by_number(db, shipment.shipmentNumber)
        if existing:
            raise HTTPException(status_code=409, detail="Shipment with this shipmentNumber already exists.")
    try:
        return create_shipment(db, shipment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shipments/{shipment_id}", response_model=ShipmentOut)
def read_shipment(shipment_id: int, db: Session = Depends(get_db)):
    db_obj = get_shipment(db, shipment_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return db_obj

@router.patch("/shipments/{shipment_id}", response_model=ShipmentOut)
def update_shipment_route(
    shipment_id: int, updates: ShipmentCreate, db: Session = Depends(get_db)
):
    db_obj = update_shipment(db, shipment_id, updates)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return db_obj

@router.delete("/shipments/{shipment_id}")
def delete_shipment_route(shipment_id: int, db: Session = Depends(get_db)):
    deleted = delete_shipment(db, shipment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return {"ok": True}

@router.post("/run-upload-shipments")
def run_upload_shipments():
    try:
        # Run the script as a subprocess in the container
        result = subprocess.run(
            ["python", "-m", "tools.upload_shipments"],
            capture_output=True, text=True, check=True
        )
        return {"status": "ok", "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Script failed: {e.stderr or str(e)}")