# vintrick-backend/app/api/routes/fruitintakes.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.fruitintake import FruitIntakeCreate, FruitIntakeOut, FruitIntakeUpdate
from app.crud import fruitintake
from app.api.deps import get_db

router = APIRouter()

@router.get("/fruit-intakes/", response_model=dict)
def list_fruitintakes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, gt=0),
    db: Session = Depends(get_db)
):
    items, total = fruitintake.get_all_fruitintakes(db, skip=skip, limit=limit)
    return {
        "items": [FruitIntakeOut.model_validate(item) for item in items],
        "total": total
    }

@router.post("/fruit-intakes/", response_model=FruitIntakeOut, status_code=201)
def create_fruitintake(
    intake: FruitIntakeCreate, db: Session = Depends(get_db)
):
    try:
        return fruitintake.create_fruitintake(db, intake)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fruit-intakes/{intake_id}", response_model=FruitIntakeOut)
def read_fruitintake(intake_id: int, db: Session = Depends(get_db)):
    db_obj = fruitintake.get_fruitintake(db, intake_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="FruitIntake not found")
    return db_obj

@router.patch("/fruit-intakes/{intake_id}", response_model=FruitIntakeOut)
def update_fruitintake(
    intake_id: int, updated: FruitIntakeUpdate, db: Session = Depends(get_db)
):
    db_obj = fruitintake.update_fruitintake(db, intake_id, updated)
    if not db_obj:
        raise HTTPException(status_code=404, detail="FruitIntake not found")
    return db_obj

@router.delete("/fruit-intakes/{intake_id}")
def delete_fruitintake(intake_id: int, db: Session = Depends(get_db)):
    deleted = fruitintake.delete_fruitintake(db, intake_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="FruitIntake not found")
    return {"ok": True}