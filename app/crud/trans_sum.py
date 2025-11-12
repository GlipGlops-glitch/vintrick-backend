# vintrick-backend/app/crud/trans_sum.py

from sqlalchemy.orm import Session
from app.models.trans_sum import (
    VesselDetails, Vessels, LossDetails,
    Additives, AdditionOps, MetricAnalysis, AnalysisOps, TransSum
)
from app.schemas.trans_sum import TransSumCreate
from typing import Optional
import logging

logger = logging.getLogger("app.crud.trans_sum")

def create_trans_sum(db: Session, trans_sum: TransSumCreate) -> TransSum:
    tx = trans_sum.model_dump()
    return insert_trans_sum_transaction(db, tx)

def safe_get(val):
    """
    Returns val if it's not None AND contains at least one non-empty value.
    Returns None if val is None or is an empty dict.
    Accepts arrays/lists and other types as present unless empty.
    """
    if val is None:
        return None
    if isinstance(val, dict):
        # If any value in the dict is not None, not empty string, not empty dict, treat as present
        for v in val.values():
            if v is not None and v != "" and v != {}:
                return val
        return None
    if isinstance(val, (list, tuple)):
        return val if len(val) > 0 else None
    return val

def insert_trans_sum_transaction(db: Session, tx: dict):
    def insert_vessel_details(d):
        d = safe_get(d)
        if not d:
            logger.info(f"No vessel details provided or vessel details are empty: {d}, skipping VesselDetails insert.")
            return None
        vd = VesselDetails(
            contentsId=d.get("contentsId"),
            batch=d.get("batch"),
            batchId=d.get("batchId"),
            volume=d.get("volume"),
            volumeUnit=d.get("volumeUnit"),
            dip=d.get("dip"),
            state=d.get("state"),
            rawTaxClass=d.get("rawTaxClass"),
            federalTaxClass=d.get("federalTaxClass"),
            stateTaxClass=d.get("stateTaxClass"),
            program=d.get("program"),
        )
        db.add(vd)
        db.flush()
        return vd.id

    def insert_vessel(vessel, is_from=True):
        vessel = safe_get(vessel)
        if not vessel:
            logger.info(f"No vessel provided or vessel is empty: {vessel}, skipping Vessels insert.")
            return None
        before_id = insert_vessel_details(vessel.get("beforeDetails"))
        after_id = insert_vessel_details(vessel.get("afterDetails"))
        v = Vessels(
            name=vessel.get("name"),
            beforeDetailsId=before_id,
            afterDetailsId=after_id,
            volOut=vessel.get("volOut") if is_from else None,
            volOutUnit=vessel.get("volOutUnit") if is_from else None,
            volIn=vessel.get("volIn") if not is_from else None,
            volInUnit=vessel.get("volInUnit") if not is_from else None
        )
        db.add(v)
        db.flush()
        return v.id

    # Insert vessels only if present and not empty
    from_vessel_id = insert_vessel(tx.get("fromVessel"), is_from=True)
    to_vessel_id = insert_vessel(tx.get("toVessel"), is_from=False)

    loss_details = safe_get(tx.get("lossDetails"))
    loss_details_id = None
    if loss_details:
        ld = LossDetails(
            volume=loss_details.get("volume"),
            volumeUnit=loss_details.get("volumeUnit"),
            reason=loss_details.get("reason"),
        )
        db.add(ld)
        db.flush()
        loss_details_id = ld.id

    # Handle Additives as part of AdditionOps
    additive = None
    if tx.get("additionOps"):
        additive = safe_get(tx["additionOps"].get("additive"))
    additive_id = None
    if additive:
        ad = Additives(
            name=additive.get("name"),
            description=additive.get("description"),
        )
        db.add(ad)
        db.flush()
        additive_id = ad.id

    addition_ops = safe_get(tx.get("additionOps"))
    addition_ops_id = None
    if addition_ops:
        # Handle lotNumbers: Vintrace sends as a list; DB expects a string
        lot_numbers = addition_ops.get("lotNumbers")
        if isinstance(lot_numbers, list):
            lot_numbers = ", ".join(str(x) for x in lot_numbers)
        elif lot_numbers is None:
            lot_numbers = None
        else:
            lot_numbers = str(lot_numbers)
        ao = AdditionOps(
            vesselId=addition_ops.get("vesselId"),
            vesselName=addition_ops.get("vesselName"),
            batchId=addition_ops.get("batchId"),
            batchName=addition_ops.get("batchName"),
            templateId=addition_ops.get("templateId"),
            templateName=addition_ops.get("templateName"),
            changeToState=addition_ops.get("changeToState"),
            volume=addition_ops.get("volume"),
            amount=addition_ops.get("amount"),
            unit=addition_ops.get("unit"),
            lotNumbers=lot_numbers,
            additiveId=additive_id,
        )
        db.add(ao)
        db.flush()
        addition_ops_id = ao.id

    analysis_ops = safe_get(tx.get("analysisOps"))
    analysis_ops_id = None
    if analysis_ops:
        ao = AnalysisOps(
            vesselId=analysis_ops.get("vesselId"),
            vesselName=analysis_ops.get("vesselName"),
            batchId=analysis_ops.get("batchId"),
            batchName=analysis_ops.get("batchName"),
            templateId=analysis_ops.get("templateId"),
            templateName=analysis_ops.get("templateName"),
        )
        db.add(ao)
        db.flush()
        analysis_ops_id = ao.id
        metrics = analysis_ops.get("metrics", [])
        if metrics:
            for metric in metrics:
                metric = safe_get(metric)
                if metric:
                    m = MetricAnalysis(
                        analysisOpsId=analysis_ops_id,
                        name=metric.get("name"),
                        value=metric.get("value"),
                        txtValue=metric.get("txtValue"),
                        unit=metric.get("unit"),
                    )
                    db.add(m)

    # Handle additionalDetails: skip empty dicts
    additional_details = tx.get("additionalDetails")
    if isinstance(additional_details, dict) and not additional_details:
        additional_details = None

    trans_sum = TransSum(
        formattedDate=tx.get("formattedDate"),
        date=tx.get("date"),
        operationId=tx.get("operationId"),
        operationTypeId=tx.get("operationTypeId"),
        operationTypeName=tx.get("operationTypeName"),
        subOperationTypeId=tx.get("subOperationTypeId"),
        subOperationTypeName=tx.get("subOperationTypeName"),
        workorder=tx.get("workorder"),
        jobNumber=str(tx.get("jobNumber")) if tx.get("jobNumber") is not None else None,
        treatment=tx.get("treatment"),
        assignedBy=tx.get("assignedBy"),
        completedBy=tx.get("completedBy"),
        winery=tx.get("winery"),
        fromVesselId=from_vessel_id,
        toVesselId=to_vessel_id,
        lossDetailsId=loss_details_id,
        additionOpsId=addition_ops_id,
        analysisOpsId=analysis_ops_id,
        additionalDetails=additional_details,
    )
    db.add(trans_sum)
    db.commit()
    db.refresh(trans_sum)
    return trans_sum

def get_all_trans_sums(db: Session, skip: int = 0, limit: int = 50):
    query = db.query(TransSum).order_by(TransSum.id.desc())
    total = query.count()
    if skip:
        query = query.offset(skip)
    if limit:
        query = query.limit(limit)
    return query.all(), total

def get_trans_sum_by_id(db: Session, id: int) -> Optional[TransSum]:
    return db.query(TransSum).filter(TransSum.id == id).first()

def update_trans_sum(db: Session, id: int, updates: TransSumCreate) -> Optional[TransSum]:
    db_obj = get_trans_sum_by_id(db, id)
    if db_obj is None:
        return None
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_trans_sum(db: Session, id: int) -> bool:
    db_obj = get_trans_sum_by_id(db, id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
        return True
    return False