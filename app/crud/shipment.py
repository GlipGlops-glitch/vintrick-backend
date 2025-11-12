# vintrick-backend/app/crud/shipment.py

from sqlalchemy.orm import Session
from app.models.shipment import (
    Shipment, ShipmentParty, ShipmentDestination, ShipmentDispatchType,
    ShipmentCarrier, WineDetail, WineBatch, DesignatedRegion, DesignatedVariety,
    DesignatedProduct, ProductCategory, Grading, WineryBuilding, WineCost
)
from app.schemas.shipment import ShipmentCreate
from typing import Optional

import json

def get_or_create(db: Session, model, defaults=None, **kwargs):
    # Flatten dicts to their 'name' field if present
    for k, v in list(kwargs.items()):
        if isinstance(v, dict):
            kwargs[k] = v.get("name") if "name" in v else None
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    params = dict((k, v) for k, v in kwargs.items())
    if defaults:
        params.update(defaults)
    instance = model(**params)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance

def create_wine_detail(db: Session, wd: dict):
    wine_batch_data = wd.get("wineBatch", {})
    designated_region = None
    designated_variety = None
    designated_product = None
    product_category = None
    grading = None
    wine_batch = None

    if wine_batch_data:
        if wine_batch_data.get("designatedRegion"):
            dr = wine_batch_data["designatedRegion"]
            designated_region = get_or_create(db, DesignatedRegion, name=dr.get("name"))
        if wine_batch_data.get("designatedVariety"):
            dv = wine_batch_data["designatedVariety"]
            designated_variety = get_or_create(db, DesignatedVariety, name=dv.get("name"))
        if wine_batch_data.get("designatedProduct"):
            dp = wine_batch_data["designatedProduct"]
            designated_product = get_or_create(db, DesignatedProduct, name=dp.get("name"))
        if wine_batch_data.get("productCategory"):
            pc = wine_batch_data["productCategory"]
            product_category = get_or_create(db, ProductCategory, name=pc.get("name"))
        if wine_batch_data.get("grading"):
            g = wine_batch_data["grading"]
            grading = get_or_create(db, Grading, scaleId=g.get("scaleId"), scaleName=g.get("scaleName"),
                                   valueId=g.get("valueId"), valueName=g.get("valueName"))
        wine_batch = get_or_create(db, WineBatch,
                                   name=wine_batch_data.get("name"),
                                   description=wine_batch_data.get("description"),
                                   vintage=wine_batch_data.get("vintage"),
                                   designatedRegion=designated_region,
                                   designatedVariety=designated_variety,
                                   designatedProduct=designated_product,
                                   productCategory=product_category,
                                   program=wine_batch_data.get("program"),
                                   grading=grading)

    winery_building = None
    if wd.get("wineryBuilding"):
        wb = wd["wineryBuilding"]
        winery_building = get_or_create(db, WineryBuilding, name=wb.get("name"))

    cost = None
    if wd.get("cost"):
        cost = get_or_create(db, WineCost, **wd["cost"])

    # Handle 'loss' field: use volume.value if dict, else float or None
    loss_val = None
    if wd.get("loss") is not None:
        if isinstance(wd["loss"], dict):
            loss_val = wd["loss"].get("volume", {}).get("value")
        elif isinstance(wd["loss"], (int, float)):
            loss_val = wd["loss"]

    # Serialize arrays and dicts as JSON strings for DB storage
    allocations_str = json.dumps(wd.get("allocations", []), ensure_ascii=False)
    metrics_str = json.dumps(wd.get("metrics", []), ensure_ascii=False)
    composition_str = json.dumps(wd.get("composition", []), ensure_ascii=False)

    wine_detail = WineDetail(
        vessel=wd.get("vessel"),
        batch=wd.get("batch"),
        volume_unit=wd.get("volume", {}).get("unit"),
        volume_value=wd.get("volume", {}).get("value"),
        loss=loss_val,
        bottlingDetails=json.dumps(wd.get("bottlingDetails", None)) if wd.get("bottlingDetails") else None,
        wineBatch=wine_batch,
        wineryBuilding=winery_building,
        cost=cost,
        allocations=allocations_str,
        metrics=metrics_str,
        composition=composition_str,
        weight=wd.get("weight"),
    )
    db.add(wine_detail)
    db.commit()
    db.refresh(wine_detail)
    return wine_detail

def create_shipment(db: Session, shipment: ShipmentCreate) -> Shipment:
    s = shipment.model_dump()

    # Nested objects
    source_obj = None
    if s.get("source"):
        src = s["source"]
        source_obj = get_or_create(db, ShipmentParty, name=src.get("name"), businessUnit=src.get("businessUnit"))

    destination_obj = None
    if s.get("destination"):
        dest = s["destination"]
        party_obj = None
        winery_val = None
        if dest.get("party"):
            party = dest["party"]
            party_obj = get_or_create(db, ShipmentParty, name=party.get("name"), businessUnit=party.get("businessUnit"))
        if dest.get("winery"):
            winery = dest["winery"]
            if isinstance(winery, dict):
                winery_val = winery.get("name")
            else:
                winery_val = winery
        destination_obj = get_or_create(db, ShipmentDestination, winery=winery_val, party=party_obj)

    dispatch_type_obj = None
    if s.get("dispatchType"):
        dt = s["dispatchType"]
        dispatch_type_obj = get_or_create(db, ShipmentDispatchType, name=dt.get("name"))

    carrier_obj = None
    if s.get("carrier"):
        cr = s["carrier"]
        carrier_obj = get_or_create(db, ShipmentCarrier, name=cr.get("name"))

    shipment_obj = Shipment(
        workOrderNumber=s.get("workOrderNumber"),
        jobNumber=s.get("jobNumber"),
        shipmentNumber=s.get("shipmentNumber"),
        type=s.get("type"),
        occurredTime=s.get("occurredTime"),
        modifiedTime=s.get("modifiedTime"),
        reference=s.get("reference"),
        freightCode=s.get("freightCode"),
        reversed=s.get("reversed"),
        source=source_obj,
        destination=destination_obj,
        dispatchType=dispatch_type_obj,
        carrier=carrier_obj
    )
    db.add(shipment_obj)
    db.commit()
    db.refresh(shipment_obj)

    wine_details = s.get("wineDetails", [])
    wine_details_objs = []
    for wd in wine_details:
        wd_obj = create_wine_detail(db, wd)
        wd_obj.shipment = shipment_obj
        db.add(wd_obj)
        wine_details_objs.append(wd_obj)
    db.commit()

    return shipment_obj

def get_shipment(db: Session, shipment_id: int) -> Optional[Shipment]:
    return db.query(Shipment).filter(Shipment.id == shipment_id).first()

def get_shipment_by_number(db: Session, shipment_number: str) -> Optional[Shipment]:
    return db.query(Shipment).filter(Shipment.shipmentNumber == shipment_number).first()

def get_all_shipments(db: Session, skip: int = 0, limit: int = 50):
    query = db.query(Shipment)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return items, total

def update_shipment(db: Session, shipment_id: int, updates: ShipmentCreate) -> Optional[Shipment]:
    db_obj = get_shipment(db, shipment_id)
    if db_obj is None:
        return None
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_shipment(db: Session, shipment_id: int) -> bool:
    db_obj = get_shipment(db, shipment_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return True
    return False