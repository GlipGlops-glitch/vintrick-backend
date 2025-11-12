# vintrick-backend/app/crud/fruitintake.py

from sqlalchemy.orm import Session
from app.models.fruitintake import FruitIntake
from app.schemas.fruitintake import FruitIntakeCreate, FruitIntakeUpdate
from datetime import datetime, timezone
from typing import Optional, List

def create_fruitintake(db: Session, intake: FruitIntakeCreate) -> FruitIntake:
    data = intake.model_dump()
    # Flatten nested objects for DB columns
    def extract(obj, field, subfield):
        if obj and getattr(obj, subfield, None):
            return getattr(obj, subfield)
        return None
    # block, owner, winery, scale, intendedProduct, carrier
    data["block_extid"] = extract(intake.block, "block", "extId")
    data["block_name"] = extract(intake.block, "block", "name")
    data["owner_extid"] = extract(intake.owner, "owner", "extId")
    data["owner_name"] = extract(intake.owner, "owner", "name")
    if intake.winery:
        data["winery_bu"] = intake.winery.businessUnit
        data["winery_name"] = intake.winery.name
    if intake.scale:
        data["scale_name"] = intake.scale.name
    if intake.gross:
        data["gross_value"] = intake.gross.value
        data["gross_unit"] = intake.gross.unit
    if intake.tare:
        data["tare_value"] = intake.tare.value
        data["tare_unit"] = intake.tare.unit
    if intake.net:
        data["net_value"] = intake.net.value
        data["net_unit"] = intake.net.unit
    if intake.intendedProduct:
        data["intendedProduct_name"] = intake.intendedProduct.name
    if intake.unitPrice:
        data["unitPrice_value"] = intake.unitPrice.value
        data["unitPrice_unit"] = intake.unitPrice.unit
    if intake.carrier:
        data["carrier_name"] = intake.carrier.name
        data["carrier_extid"] = intake.carrier.extId
    data["metrics"] = [metric.model_dump() for metric in (intake.metrics or [])]
    data["last_modified"] = datetime.now(timezone.utc)
    db_obj = FruitIntake(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_fruitintake(db: Session, intake_id: int) -> Optional[FruitIntake]:
    return db.query(FruitIntake).filter(FruitIntake.id == intake_id).first()

def get_all_fruitintakes(db: Session, skip: int = 0, limit: int = 50):
    query = db.query(FruitIntake).order_by(FruitIntake.dateOccurred.desc(), FruitIntake.id.desc())
    total = query.count()
    if skip:
        query = query.offset(skip)
    if limit:
        query = query.limit(limit)
    return query.all(), total

def update_fruitintake(db: Session, intake_id: int, updates: FruitIntakeUpdate) -> Optional[FruitIntake]:
    db_obj = get_fruitintake(db, intake_id)
    if db_obj is None:
        return None
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(db_obj, key):
            setattr(db_obj, key, value)
    db_obj.last_modified = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_fruitintake(db: Session, intake_id: int) -> bool:
    db_obj = get_fruitintake(db, intake_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return True
    return False