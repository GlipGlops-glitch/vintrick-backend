# vintrick-backend/app/api/routes/trans_sum.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.trans_sum import TransSumCreate, TransSumOut
from app.crud import trans_sum as trans_sum_crud
from app.api.deps import get_db

router = APIRouter()

@router.get("/trans_sum/", response_model=dict)
def list_trans_sums(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, gt=0),
    db: Session = Depends(get_db)
):
    try:
        items, total = trans_sum_crud.get_all_trans_sums(db, skip=skip, limit=limit)
        return {
            "items": [TransSumOut.model_validate(item) for item in items],
            "total": total
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trans_sums: {str(e)}")

@router.post("/trans_sum/", response_model=TransSumOut)
def create_trans_sum(
    payload: TransSumCreate, db: Session = Depends(get_db)
):
    try:
        obj = trans_sum_crud.create_trans_sum(db, payload)
        return TransSumOut.model_validate(obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create trans_sum: {str(e)}")

@router.get("/trans_sum/{id}", response_model=TransSumOut)
def read_trans_sum(id: int, db: Session = Depends(get_db)):
    try:
        db_obj = trans_sum_crud.get_trans_sum_by_id(db, id)
        if db_obj is None:
            raise HTTPException(status_code=404, detail="TransSum not found")
        return TransSumOut.model_validate(db_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read trans_sum: {str(e)}")

@router.patch("/trans_sum/{id}", response_model=TransSumOut)
def update_trans_sum(
    id: int, payload: TransSumCreate, db: Session = Depends(get_db)
):
    try:
        db_obj = trans_sum_crud.update_trans_sum(db, id, payload)
        if not db_obj:
            raise HTTPException(status_code=404, detail="TransSum not found")
        return TransSumOut.model_validate(db_obj)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update trans_sum: {str(e)}")

@router.delete("/trans_sum/{id}")
def delete_trans_sum(id: int, db: Session = Depends(get_db)):
    try:
        deleted = trans_sum_crud.delete_trans_sum(db, id)
        if not deleted:
            raise HTTPException(status_code=404, detail="TransSum not found")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete trans_sum: {str(e)}")